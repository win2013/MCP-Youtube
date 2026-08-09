
"""Tests for POST request hanging issue"""
import pytest
import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_youtube.mcp_server import EnvelopeMiddleware


class TestPostRequestHang:
    """Tests for POST request hanging in middleware"""
    
    @pytest.mark.asyncio
    async def test_post_with_empty_body_does_not_hang(self):
        """Test that POST requests with empty body don't hang"""
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/mcp",
            "headers": [(b"content-type", b"application/json")],
            "client": ("127.0.0.1", 12345),
            "server": ("0.0.0.0", 9090),
        }
        
        received_count = [0]
        
        async def receive():
            received_count[0] += 1
            # Return empty body with more_body=False to indicate request is complete
            return {
                "type": "http.request",
                "body": b"",
                "more_body": False
            }
        
        sent_messages = []
        
        async def send(message):
            sent_messages.append(message)
        
        # Create a simple app that just returns 200
        async def simple_app(scope, receive, send):
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"application/json"]],
            })
            await send({
                "type": "http.response.body",
                "body": b'{"status": "ok"}',
            })
        
        middleware = EnvelopeMiddleware(simple_app)
        
        # This should not hang - set a timeout to detect hanging
        try:
            async with asyncio.timeout(2):  # Should complete within 2 seconds
                await middleware(scope, receive, send)
        except asyncio.TimeoutError:
            pytest.fail("Middleware hung while processing POST request with empty body")
        
        # Verify we only called receive once (not multiple times)
        assert received_count[0] == 1, f"Expected receive to be called once, but was called {received_count[0]} times"
    
    @pytest.mark.asyncio
    async def test_post_with_json_body_completes(self):
        """Test that POST requests with JSON body complete successfully"""
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/mcp",
            "headers": [(b"content-type", b"application/json")],
            "client": ("127.0.0.1", 12345),
            "server": ("0.0.0.0", 9090),
        }
        
        request_body = json.dumps({
            "jsonrpc": "2.0",
            "method": "test",
            "id": 1
        }).encode()
        
        received_count = [0]
        
        async def receive():
            received_count[0] += 1
            if received_count[0] == 1:
                return {
                    "type": "http.request",
                    "body": request_body,
                    "more_body": False
                }
            # Should not be called again
            await asyncio.sleep(10)
            return {"type": "http.request", "body": b"", "more_body": False}
        
        sent_messages = []
        
        async def send(message):
            sent_messages.append(message)
        
        async def simple_app(scope, receive, send):
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"application/json"]],
            })
            await send({
                "type": "http.response.body",
                "body": b'{"status": "ok"}',
            })
        
        middleware = EnvelopeMiddleware(simple_app)
        
        # Should complete without hanging
        try:
            async with asyncio.timeout(2):
                await middleware(scope, receive, send)
        except asyncio.TimeoutError:
            pytest.fail("Middleware hung while processing POST request with JSON body")
        
        # Verify we only called receive once
        assert received_count[0] == 1, f"Expected receive to be called once, but was called {received_count[0]} times"