
"""MCP Server implementation with SSE, TCP, and STDIO transports"""
"""Edwin A. Hernandez, PhD"""

import asyncio
import os
import secrets
import logging
import subprocess
import sys
from typing import Optional, Any
from dotenv import load_dotenv
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# Import ASGI types
try:
    from starlette.types import Scope, Receive, Send
except ImportError:
    # Fallback for older starlette versions
    Scope = Any
    Receive = Any
    Send = Any

load_dotenv('.env_yt')

# Function to generate session ID
def generate_session_id() -> str:
    """Generate a unique session ID for MCP connections"""
    return secrets.token_urlsafe(16)

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
from starlette.middleware.cors import CORSMiddleware
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
    version="0.2.0",
    instructions="A Model Context Protocol server for YouTube that retrieves and processes video content."
)

# Add CORS middleware to allow cross-origin requests
# This enables the MCP server to accept requests from any origin
# Configure CORS with required MCP headers
cors_middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],                    # or list the exact origin of your llama WebUI
        allow_credentials=True,                 # often needed
        allow_methods=["GET", "POST", "OPTIONS", "DELETE"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "mcp-protocol-version",
            "mcp-session-id",
            "X-Requested-With",
            "*"                                 # some clients send extra headers
        ],
        expose_headers=["mcp-session-id"],
        max_age=86400,
    )
]

# Pass middleware to the http_app
app = mcp.http_app(middleware=cors_middleware)


# Token for authentication
TOKEN_KEY = os.environ.get("MCP_TOKEN_KEY") or secrets.token_urlsafe(32)
MCP_PORT = int(os.environ.get("MCP_PORT", 9090))




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
    
    # FastMCP's streamable-http transport handles CORS and request processing internally
    # No custom middleware needed - FastMCP handles it automatically
    
   # mcp.run(
   #     transport="streamable-http", 
   #     host=host, 
   #     port=port,
   #     json_response=json_response,
   # )

    uvicorn.run(
        app,
        host=host,
        port=port,
        # log_level="info",          # optional
        # reload=True,               # optional for development
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