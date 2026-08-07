
"""MCP Server implementation with SSE, TCP, and STDIO transports"""
"""Edwin A. Hernandez, PhD"""

import asyncio
import os
import secrets
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv('.env_yt')

from fastmcp import FastMCP
from fastmcp.utilities.logging import get_logger

from .youtube_client import YouTubeClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

# Create FastMCP server
mcp = FastMCP(
    name="YouTube MCP Server",
    version="0.1.0",
    instructions="A Model Context Protocol server for YouTube that retrieves and processes video content."
)

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
        Dictionary containing video details
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


def run_tcp_transport(host: str = "0.0.0.0", port: int = MCP_PORT):
    """Run MCP server with TCP transport"""
    logger.info(f"Starting TCP transport on {host}:{port}")
    logger.info(f"Token key: {TOKEN_KEY}")
    mcp.run(transport="tcp", host=host, port=port)


def run_stdio_transport():
    """Run MCP server with STDIO transport"""
    logger.info("Starting STDIO transport")
    logger.info(f"Token key: {TOKEN_KEY}")
    mcp.run(transport="stdio")


def run_sse_transport(host: str = "0.0.0.0", port: int = MCP_PORT):
    """Run MCP server with SSE transport"""
    logger.info(f"Starting SSE transport on {host}:{port}")
    logger.info(f"Token key: {TOKEN_KEY}")
    mcp.run(transport="sse", host=host, port=port)


def run_all_transports(host: str = "0.0.0.0", port: int = MCP_PORT):
    """Run MCP server with all transports"""
    logger.info(f"Starting MCP server on {host}:{port}")
    logger.info(f"Token key: {TOKEN_KEY}")
    
    # FastMCP doesn't support running multiple transports simultaneously
    # Run them sequentially - each will block until stopped
    import threading
    
    def run_transport(transport_name: str, **kwargs):
        mcp.run(transport=transport_name, **kwargs)
    
    # Start each transport in a separate thread
    threads = []
    tcp_thread = threading.Thread(target=run_transport, args=("tcp",), kwargs={"host": host, "port": port}, daemon=True)
    sse_thread = threading.Thread(target=run_transport, args=("sse",), kwargs={"host": host, "port": port}, daemon=True)
    stdio_thread = threading.Thread(target=run_transport, args=("stdio",), daemon=True)
    
    threads.append(tcp_thread)
    threads.append(sse_thread)
    threads.append(stdio_thread)
    
    for t in threads:
        t.start()
    
    # Keep main thread alive
    for t in threads:
        t.join()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run YouTube MCP Server")
    parser.add_argument(
        "--transport",
        choices=["tcp", "stdio", "sse", "all"],
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
    
    if args.transport == "tcp":
        run_tcp_transport(args.host, args.port)
    elif args.transport == "stdio":
        run_stdio_transport()
    elif args.transport == "sse":
        run_sse_transport(args.host, args.port)
    elif args.transport == "all":
        run_all_transports(args.host, args.port)
    else:
        logger.error(f"Unknown transport: {args.transport}")
        exit(1)