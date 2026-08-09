
"""MCP Server implementation with SSE, TCP, and STDIO transports"""
"""Edwin A. Hernandez, PhD"""

import asyncio
import os
import secrets
import logging
import subprocess
import sys
from typing import Optional
from dotenv import load_dotenv

load_dotenv('.env_yt')

# Patch the _check_accept_headers function to accept application/json, text/event-stream or both BEFORE importing anything else
import mcp.server.streamable_http as streamable_http_module

def patched_check_accept_headers(self, request):
    """Check if the request accepts the required media types.
    
    Accepts requests with:
    - application/json (for JSON-RPC)
    - text/event-stream (for SSE)
    - Both together (for streamable HTTP transport)
    - Wildcards (*/* or *)
    """
    accept_header = request.headers.get("accept", "")
    accept_types = [media_type.strip().lower() for media_type in accept_header.split(",")]
    
    # Check for wildcards
    has_wildcard = any(media_type == '*/*' or media_type == '*' for media_type in accept_types)
    
    # Original check for specific types
    has_json = any('application/json' in media_type or has_wildcard for media_type in accept_types)
    has_sse = any('text/event-stream' in media_type or has_wildcard for media_type in accept_types)
    
    return has_json, has_sse

# Apply the patch to StreamableHTTPServerTransport
if hasattr(streamable_http_module, 'StreamableHTTPServerTransport'):
    streamable_http_module.StreamableHTTPServerTransport._check_accept_headers = patched_check_accept_headers
    print("Patched _check_accept_headers to accept json, event-stream, or both", file=sys.stderr)

from fastmcp import FastMCP
from fastmcp.utilities.logging import get_logger
from starlette.responses import JSONResponse
from typing import Any

from mcp_youtube.youtube_client import YouTubeClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

# Store the FastMCP app instance for handling envelope format
_mcp_app: Any = None

# Create FastMCP server
mcp = FastMCP(
    name="YouTube MCP Server",
    version="0.1.0",
    instructions="A Model Context Protocol server for YouTube that retrieves and processes video content."
)


# Removed @mcp.custom_route handler - the middleware will handle envelope extraction
# FastMCP will now process the extracted JSON-RPC directly


def handle_envelope_request(request: dict) -> dict | None:
    """
    Handle Llama.cpp envelope format and return the extracted JSON-RPC request.
    
    If the request is already in JSON-RPC format, returns it as-is.
    If the request is in envelope format, extracts and returns the JSON-RPC.
    Otherwise, returns None.
    """
    # First check if it's already JSON-RPC format
    if isinstance(request, dict):
        if "jsonrpc" in request and "method" in request:
            return request
    
    # Check if this is the Llama.cpp envelope format
    if isinstance(request, dict):
        if "serverName" in request and "request" in request:
            request_obj = request.get("request", {})
            body_obj = request_obj.get("body", {})
            logger.info(f"Checking envelope format, body: {body_obj}")
            # Check if body contains the actual JSON-RPC as a string
            if body_obj.get("kind") == "string" and "value" in body_obj:
                try:
                    import json
                    return json.loads(body_obj["value"])
                except (json.JSONDecodeError, TypeError):
                    return None
            
            # Check if body has direct JSON-RPC structure
            if "value" not in body_obj and isinstance(body_obj, dict):
                # Maybe the envelope structure is different - check for JSON-RPC fields
                if "jsonrpc" in body_obj and "method" in body_obj:
                    return body_obj
    
    return None


# Token for authentication
TOKEN_KEY = os.environ.get("MCP_TOKEN_KEY") or secrets.token_urlsafe(32)
MCP_PORT = int(os.environ.get("MCP_PORT", 9090))


def handle_envelope_envelope(body: dict, http_body_bytes: bytes | None = None) -> dict | None:
    """
    Handle Llama.cpp envelope format and extract the actual JSON-RPC request.
    
    Returns the extracted JSON-RPC dict if envelope format detected, None otherwise.
    
    Args:
        body: The parsed JSON body of the envelope request
        http_body_bytes: Raw HTTP request body bytes (used when kind="string" but value is missing)
    """
    if not isinstance(body, dict):
        return None
    
    # First check if the body itself is already a JSON-RPC request
    if "jsonrpc" in body and "method" in body:
        return body
    
    # Check if this is the Llama.cpp envelope format
    if "serverName" in body and "request" in body:
        request_obj = body.get("request", {})
        body_obj = request_obj.get("body", {})
        logger.info(f" handle_envelop: Checking envelope format, body: {request_obj}")

        # Check if body contains the actual JSON-RPC as a string in 'value' field
        if isinstance(body_obj, dict):
            if body_obj.get("kind") == "string" and "value" in body_obj:
                try:
                    import json
                    actual_request = json.loads(body_obj["value"])
                    return actual_request
                except (json.JSONDecodeError, TypeError):
                    pass
            
            # Check if body is already JSON-RPC format
            if isinstance(body_obj, dict) and "jsonrpc" in body_obj and "method" in body_obj:
                return body_obj
            
            # Handle case where kind="string" but value is missing
            # The JSON-RPC might be in the HTTP request body directly
            if body_obj.get("kind") == "string" and "value" not in body_obj and http_body_bytes:
                try:
                    import json
                    actual_request = json.loads(http_body_bytes.decode("utf-8"))
                    if "jsonrpc" in actual_request and "method" in actual_request:
                        logger.info(f"Extracted JSON-RPC from HTTP body (kind=string, no value)")
                        return actual_request
                except (json.JSONDecodeError, TypeError):
                    pass
    
    return None


# Custom middleware to handle envelope format before fastmcp processes
class EnvelopeMiddleware:
    """Middleware to handle Llama.cpp envelope format before fastmcp processing."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """Intercept requests and handle envelope format."""
        import json
        
        logger.info(f"EnvelopeMiddleware called, scope type: {scope.get('type')}")
        
        if scope["type"] == "http":
            # Read the request body once
            body_bytes = b""
            more_body = True
            
            while more_body:
                message = await receive()
                body_bytes += message.get("body", b"")
                more_body = message.get("more_body", False)
            
            logger.info(f"Received body bytes: {body_bytes[:200]}")
            
            # Determine the final body (either extracted or original)
            final_body_bytes = body_bytes
            
            try:
                body = json.loads(body_bytes.decode("utf-8"))
                
                logger.info(f"Parsed JSON body: {body}")
                
                # Check if this is an envelope format
                extracted = handle_envelope_envelope(body, body_bytes)
                
                if extracted is not None:
                    logger.info(f"Extracted JSON-RPC from Llama.cpp envelope")
                    logger.info(f"Extracted JSON-RPC: {extracted}")
                    
                    # Use the extracted JSON-RPC as the body
                    final_body_bytes = json.dumps(extracted).encode("utf-8")
                    logger.info(f"Final body bytes (extracted): {final_body_bytes}")
                else:
                    logger.info("No envelope format detected, using original body")
            except json.JSONDecodeError as e:
                # Not valid JSON, use original body
                logger.warning(f"Failed to parse JSON: {e}")
            
            # Update Content-Length header to match final body size
            # Remove existing Content-Length and Transfer-Encoding headers
            new_headers = [
                (k, v) for k, v in scope["headers"]
                if k.lower() not in [b"content-length", b"transfer-encoding"]
            ]
            new_headers.append((b"content-length", str(len(final_body_bytes)).encode()))
            scope["headers"] = new_headers
            
            # Always create a new receive function with the final body
            async def new_receive():
                return {
                    "type": "http.request",
                    "body": final_body_bytes,
                    "more_body": False
                }
            
            # Create a wrapper for send to handle the response
            original_send = send
            
            async def wrapped_send(message):
                if message["type"] == "http.response.start":
                    logger.info(f"Response start: status={message.get('status')}")
                elif message["type"] == "http.response.body":
                    logger.info(f"Response body: body={message.get('body', b'')[:200]}")
                
                await original_send(message)
            
            # Call the original app with the new receive and send
            try:
                await self.app(scope, new_receive, wrapped_send)
            except Exception as e:
                logger.error(f"Error in middleware: {e}", exc_info=True)
                # Send error response if something goes wrong
                await wrapped_send({
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [[b"content-type", b"application/json"]],
                })
                await wrapped_send({
                    "type": "http.response.body",
                    "body": b'{"error": "Internal server error"}',
                })
        else:
            await self.app(scope, receive, send)

# Store YouTube client for reuse
_youtube_client: Optional[YouTubeClient] = None


def get_youtube_client() -> YouTubeClient:
    """Get or create YouTube client instance"""
    global _youtube_client
    if _youtube_client is None:
        api_key = os.environ.get("YOUTUBE_API_KEY")
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is required")
        _youtube_client = YouTubeClient(api_key=api_key)
    return _youtube_client


def handle_llama_cpp_envelope(request_body: dict) -> dict | None:
    """
    Handle Llama.cpp 2026 envelope format and extract the actual JSON-RPC request.
    
    Llama.cpp sends a wrapper format:
    {
      "serverName": "...",
      "request": {
        "url": "...",
        "method": "POST",
        "headers": {...},
        "body": {
          "kind": "string",
          "size": 189,
          "value": "{\"jsonrpc\":\"2.0\",\"method\":\"initialize\",...}"
        }
      }
    }
    
    Returns the extracted JSON-RPC body dict, or None if not envelope format.
    """
    if not isinstance(request_body, dict):
        return None
    
    # Check if this is the Llama.cpp envelope format
    if "serverName" in request_body and "request" in request_body:
        request_obj = request_body.get("request", {})
        body_obj = request_obj.get("body", {})
        logger.info(f"handle_llama_cpp_envelope: Checking envelope format, body: {body_obj}")        
        # Check if body contains the actual JSON-RPC as a string
        if body_obj.get("kind") == "string" and "value" in body_obj:
            try:
                import json
                actual_request = json.loads(body_obj["value"])
                logger.info(f"Extracted JSON-RPC from Llama.cpp envelope: {actual_request}")
                return actual_request
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Failed to parse extracted JSON-RPC: {body_obj['value']}")
                return None
        
    return None


def extract_jsonrpc_from_request(request_body: dict) -> dict:
    """
    Extract the actual JSON-RPC request from various formats.
    Handles both standard JSON-RPC and Llama.cpp envelope format.
    
    Supports MCP protocol versions 2024, 2025, and 2026.
    """
    # First check if it's already a standard JSON-RPC request
    
    if isinstance(request_body, dict):
        if "jsonrpc" in request_body and request_body["jsonrpc"] == "2.0":
            if "method" in request_body and "id" in request_body:
                return request_body
           
      
    # Try to extract from Llama.cpp envelope format
    # extracted = handle_llama_cpp_envelope(request_body)
    # if extracted is not None:
    #    return extracted
    
    # Return original if no transformation needed
    return request_body


@mcp.tool()
async def get_video_details(video_id: str) -> dict:
    """Get detailed information about a YouTube video
    
    Args:
        video_id: YouTube video ID or URL
        
    Returns:
        Dictionary containigng video details
    """
    client = get_youtube_client()
    video_id_clean = client.extract_video_id(video_id) or video_id
    return await client.get_video_details(video_id_clean)


@mcp.tool()
async def get_transcript(video_id: str) -> list:
    """Get transcript for a YouTube video
    
    Args:
        video_id: YouTube video ID or URL
        
    Returns:
        List of transcript segments with text and timestamps
    """
    client = get_youtube_client()
    video_id_clean = client.extract_video_id(video_id) or video_id
    return await client.get_transcript(video_id_clean)


@mcp.tool()
async def get_similar_videos(
    video_id: str, 
    max_results: int = 10
) -> list:
    """Get similar videos to a given YouTube video
    
    Args:
        video_id: YouTube video ID or URL
        max_results: Maximum number of similar videos to return (default: 10)
        
    Returns:
        List of similar video details
    """
    client = get_youtube_client()
    video_id_clean = client.extract_video_id(video_id) or video_id
    return await client.get_similar_videos(video_id_clean, max_results=max_results)


@mcp.tool()
async def search_videos(
    query: str, 
    max_results: int = 10
) -> list:
    """Search for YouTube videos
    
    Args:
        query: Search query string
        max_results: Maximum number of results (default: 10)
        
    Returns:
        List of video details matching the search
    """
    client = get_youtube_client()
    return await client.search_videos(query, max_results=max_results)


def run_http_transport(host: str = "0.0.0.0", port: int = MCP_PORT, json_response: bool = False):
    """Run MCP server with HTTP transport (streamable-http)
    
    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: MCP_PORT)
        json_response: If True, return JSON responses and close connection.
                      If False (default), use SSE streaming for long-lived connections.
    """
    logger.info(f"Starting HTTP transport on {host}:{port}")
    logger.info(f"Token key: {TOKEN_KEY}")
    logger.info(f"JSON response mode: {json_response}")
    
    # FastMCP's add_middleware adds to the MCP message middleware chain,
    # not the ASGI/HTTP middleware chain. We need to pass ASGI middleware directly
    # to the HTTP app.
    
    # Create an ASGI-compatible wrapper for our EnvelopeMiddleware
    # FastMCP's run_http_async accepts middleware parameter for ASGI middleware
    
    logger.info("Adding EnvelopeMiddleware as ASGI middleware")
    
    # Import Starlette's Middleware class to wrap our ASGI middleware
    from starlette.middleware import Middleware
    
    # Run the server with streamable-http transport and pass the middleware
    # Wrap our middleware in Starlette's Middleware class
    mcp.run(
        transport="streamable-http", 
        host=host, 
        port=port,
        json_response=json_response,
        middleware=[Middleware(EnvelopeMiddleware)]  # Wrap in Starlette's Middleware
    )


def run_sse_transport(host: str = "0.0.0.0", port: int = MCP_PORT):
    """Run MCP server with SSE transport"""
    logger.info(f"Starting SSE transport on {host}:{port}")
    logger.info(f"Token key: {TOKEN_KEY}")
    mcp.run(transport="sse", host=host, port=port)


def run_stdio_transport():
    """Run MCP server with STDIO transport"""
    logger.info("Starting STDIO transport")
    logger.info(f"Token key: {TOKEN_KEY}")
    mcp.run(transport="stdio")


def run_all_transports(host: str = "0.0.0.0", port: int = MCP_PORT):
    """Run MCP server with all transports (streamable-http, SSE, and STDIO)."""
    logger.info(f"Starting all transports on {host}:{port}")
    logger.info(f"Token key: {TOKEN_KEY}")

    env = os.environ.copy()
    env["MCP_PORT"] = str(port)

    commands = [
        (
            "streamable-http",
            [sys.executable, __file__, "--transport", "http", "--host", host, "--port", str(port)],
        ),
        (
            "sse",
            [sys.executable, __file__, "--transport", "sse", "--host", host, "--port", str(port)],
        ),
        (
            "stdio",
            [sys.executable, __file__, "--transport", "stdio"],
        ),
    ]

    processes = []
    try:
        for transport_name, command in commands:
            logger.info(f"Starting {transport_name} transport")
            process = subprocess.Popen(
                command,
                env=env,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
            processes.append((transport_name, process))

        for transport_name, process in processes:
            process.wait()
    except KeyboardInterrupt:
        logger.info("Shutting down all transports")
    finally:
        for transport_name, process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run YouTube MCP Server")
    parser.add_argument(
        "--transport",
        choices=["http", "stdio", "sse", "all"],
        default="all",
        help="Transport method to use"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to listen on (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=MCP_PORT,
        help=f"Port to listen on (default: {MCP_PORT})"
    )
    
    args = parser.parse_args()
    
    if args.transport == "http":
        run_http_transport(args.host, args.port)
    elif args.transport == "stdio":
        run_stdio_transport()
    elif args.transport == "sse":
        run_sse_transport(args.host, args.port)
    elif args.transport == "all":
        run_all_transports(args.host, args.port)
    else:
        logger.error(f"Unknown transport: {args.transport}")
        exit(1)