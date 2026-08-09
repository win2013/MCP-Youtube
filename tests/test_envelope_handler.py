
"""Tests for Llama.cpp envelope handler"""
import pytest
import json
from mcp_youtube.mcp_server import handle_envelope_envelope, handle_envelope_request


class TestEnvelopeExtraction:
    """Tests for envelope extraction logic"""
    
    def test_envelope_without_value_field_returns_none(self):
        """Test that envelope without value field and no http_body_bytes returns None"""
        envelope = {
            "serverName": "test-server",
            "request": {
                "url": "http://192.168.1.121:9091/mcp",
                "body": {
                    "kind": "string",
                    "size": 100
                }
            }
        }
        
        result = handle_envelope_envelope(envelope)
        assert result is None
    
    def test_envelope_without_value_field_with_http_body(self):
        """Test that envelope without value field extracts from http_body_bytes"""
        envelope = {
            "serverName": "test-server",
            "request": {
                "url": "http://192.168.1.121:9091/mcp",
                "body": {
                    "kind": "string",
                    "size": 100
                }
            }
        }
        
        http_body = b'{"jsonrpc":"2.0","method":"test","id":1}'
        result = handle_envelope_envelope(envelope, http_body)
        assert result is not None
        assert result["jsonrpc"] == "2.0"
        assert result["method"] == "test"
        assert result["id"] == 1
    
    def test_envelope_with_value_field(self):
        """Test envelope with value field containing JSON-RPC"""
        envelope = {
            "serverName": "test-server",
            "request": {
                "url": "http://192.168.1.121:9091/mcp",
                "body": {
                    "kind": "string",
                    "size": 100,
                    "value": '{"jsonrpc":"2.0","method":"test","id":1}'
                }
            }
        }
        
        result = handle_envelope_envelope(envelope)
        assert result is not None
        assert result["jsonrpc"] == "2.0"
        assert result["method"] == "test"
        assert result["id"] == 1


class TestEnvelopeHandler:
    """Tests for Llama.cpp envelope format handling"""
    
    def test_llama_cpp_envelope_format(self):
        """Test extracting JSON-RPC from Llama.cpp envelope format"""
        envelope = {
            "serverName": "8kw9uol19qn",
            "request": {
                "url": "http://192.168.1.121:9091/mcp",
                "method": "POST",
                "headers": {
                    "accept": "application/json, text/event-stream",
                    "content-type": "application/json"
                },
                "body": {
                    "kind": "string",
                    "size": 189,
                    "value": "{\"jsonrpc\":\"2.0\",\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2025-11-25\",\"capabilities\":{}},\"id\":1}"
                },
                "jsonRpcMethods": ["initialize"]
            }
        }
        
        result = handle_envelope_envelope(envelope)
        
        assert result is not None
        assert result["jsonrpc"] == "2.0"
        assert result["method"] == "initialize"
        assert result["id"] == 1
        assert result["params"]["protocolVersion"] == "2025-11-25"
    
    def test_llama_cpp_envelope_with_2026_version(self):
        """Test envelope with MCP 2026 protocol version"""
        envelope = {
            "serverName": "test-server",
            "request": {
                "body": {
                    "kind": "string",
                    "value": "{\"jsonrpc\":\"2.0\",\"method\":\"ping\",\"params\":{},\"id\":2}"
                }
            }
        }
        
        result = handle_envelope_envelope(envelope)
        
        assert result is not None
        assert result["jsonrpc"] == "2.0"
        assert result["method"] == "ping"
        assert result["id"] == 2
    
    def test_llama_cpp_envelope_with_2024_version(self):
        """Test envelope with MCP 2024 protocol version"""
        envelope = {
            "serverName": "test-server",
            "request": {
                "body": {
                    "kind": "string",
                    "value": "{\"jsonrpc\":\"2.0\",\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\"},\"id\":1}"
                }
            }
        }
        
        result = handle_envelope_envelope(envelope)
        
        assert result is not None
        assert result["params"]["protocolVersion"] == "2024-11-05"
    
    def test_non_envelope_format_returns_jsonrpc(self):
        """Test that standard JSON-RPC request is returned as-is"""
        standard_jsonrpc = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {},
            "id": 1
        }
        
        result = handle_envelope_envelope(standard_jsonrpc)
        
        assert result is not None
        assert result["jsonrpc"] == "2.0"
        assert result["method"] == "initialize"
        assert result["id"] == 1
    
    def test_invalid_json_in_body(self):
        """Test handling of invalid JSON in body"""
        envelope = {
            "serverName": "test",
            "request": {
                "body": {
                    "kind": "string",
                    "value": "invalid json {"
                }
            }
        }
        
        result = handle_envelope_envelope(envelope)
        
        assert result is None
    
    def test_missing_value_field(self):
        """Test envelope without value field"""
        envelope = {
            "serverName": "test",
            "request": {
                "body": {
                    "kind": "string"
                }
            }
        }
        
        result = handle_envelope_envelope(envelope)
        
        assert result is None
    
    def test_extract_jsonrpc_standard_format(self):
        """Test extract function with standard JSON-RPC"""
        standard_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"protocolVersion": "2025-11-25"},
            "id": 1
        }
        
        result = handle_envelope_request(standard_request)
        
        assert result == standard_request
    
    def test_extract_jsonrpc_envelope_format(self):
        """Test extract function with envelope format"""
        envelope = {
            "serverName": "test",
            "request": {
                "body": {
                    "kind": "string",
                    "value": "{\"jsonrpc\":\"2.0\",\"method\":\"ping\",\"id\":1}"
                }
            }
        }
        
        result = handle_envelope_request(envelope)
        
        assert result["jsonrpc"] == "2.0"
        assert result["method"] == "ping"
        assert result["id"] == 1
    
    def test_extract_jsonrpc_non_jsonrpc_format(self):
        """Test extract function with non-JSON-RPC format"""
        non_jsonrpc = {
            "some": "data",
            "not": "jsonrpc"
        }
        
        result = handle_envelope_request(non_jsonrpc)
        
        assert result is None