"""MCP-Youtube - Modern Context Protocol server for YouTube"""

__version__ = "0.1.0"

# Expose MCP server
from .mcp_server import mcp, TOKEN_KEY, MCP_PORT, get_youtube_client

__all__ = [
    "mcp", 
    "TOKEN_KEY", 
    "MCP_PORT", 
    "get_youtube_client",
    "handle_envelope_envelope",
    "handle_envelope_request",
]
