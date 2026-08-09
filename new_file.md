
# MCP Request Fix for Llama.cpp

## Problem
The Llama.cpp MCP client is sending requests in envelope format without the required `value` field containing the actual JSON-RPC request.

## Error Analysis
The server is receiving:
```json
{
  "serverName": "nu5vkp0km3",
  "request": {
    "url": "http://192.168.1.121:9091/mcp",
    "method": "POST",
    "headers": {
      "accept": "application/json, text/event-stream",
      "content-type": "application/json"
    },
    "body": {
      "kind": "string",
      "size": 189
    },
    "jsonRpcMethods": ["initialize"]
  }
}
```

But the server is looking for `jsonrpc`, `id`, and `method` in the request body, which aren't there because the actual JSON-RPC request is missing from the `value` field.

## Correct Request Format
The request should include the actual JSON-RPC request as a string in the `value` field:

```json
{
  "serverName": "nu5vkp0km3",
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
```

## Key Changes
- Added the `value` field containing the actual JSON-RPC request as a properly escaped string
- The JSON-RPC payload includes required fields: `jsonrpc`, `method`, and `id`
- The `size` field should match the actual byte size of the JSON-RPC string

## Using curl with Timeout

**Important:** All curl commands include `--max-time 30` to prevent hanging requests. Without this timeout option, curl commands may hang indefinitely if the server is unresponsive or the connection is blocked.

## Corrected curl Command (with timeout)

**Important:** For Exa AI MCP server compatibility, the request must include an `Accept` header with BOTH `application/json` and `text/event-stream`:

```bash
curl -v --max-time 30 http://192.168.1.121:9091/mcp \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{
  "serverName": "nu5vkp0km3",
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
}'
```
# Correct MCP Initialize Request

## Issue
The user was getting validation errors because the JSON-RPC message wasn't properly formatted in the envelope.

## Correct Request Format

The envelope format requires:
1. `serverName`: The name of your server
2. `request`: The request object containing:
   - `body`: With `kind`, `size`, and `value` fields
   - `value`: A **string** containing the JSON-RPC request
   - `jsonRpcMethods`: Array of methods the server supports

## Working curl Command (with timeout)

**Important:** For Exa AI MCP server compatibility, the request must include an `Accept` header with BOTH `application/json` and `text/event-stream`:

```bash
curl -v --max-time 30 http://192.168.1.121:9091/mcp \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{
  "serverName": "nu5vkp0km3",
  "request": {
    "url": "http://192.168.1.121:9091/mcp",
    "method": "POST",
    "headers": {
      "accept": "application/json, text/event-stream",
      "content-type": "application/json"
    },
    "body": {
      "kind": "string",
      "size": 123,
      "value": "{\"jsonrpc\":\"2.0\",\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2025-11-25\",\"capabilities\":{}},\"id\":1}"
    },
    "jsonRpcMethods": ["initialize"]
  }
}'
```

## Key Points

1. The `value` field must contain a **string** (not an object) with the JSON-RPC message
2. The JSON-RPC message inside `value` must include all required fields: `jsonrpc`, `method`, `id`
3. The `size` field should match the byte length of the JSON-RPC string in `value`
4. All quotes inside the `value` string must be escaped with backslashes

## Python Script Alternative

If curl escaping continues to be problematic, use a Python script with timeout:

```python
import requests
import json

envelope = {
    "serverName": "nu5vkp0km3",
    "request": {
        "url": "http://192.168.1.121:9091/mcp",
        "method": "POST",
        "headers": {
            "accept": "application/json, text/event-stream",
            "content-type": "application/json"
        },
        "body": {
            "kind": "string",
            "size": 123,
            "value": json.dumps({
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {}
                },
                "id": 1
            })
        },
        "jsonRpcMethods": ["initialize"]
    }
}

# Add timeout to prevent hanging requests (30 seconds for connection, 30 seconds for response)
response = requests.post("http://192.168.1.121:9091/mcp", json=envelope, timeout=30)
print(response.text)
```