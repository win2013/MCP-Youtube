
# Fix for Llama.cpp MCP Request Validation Error

## Problem
You're getting a validation error because your Llama.cpp MCP request is missing the `value` field in the body that should contain the actual JSON-RPC request.

## Current Request (Incorrect)
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

## Issue
The body object is missing the `value` field. According to the Llama.cpp envelope format and the code in `mcp_server.py`, the `body.value` field should contain the actual JSON-RPC request as a string.

## Corrected Request
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
- Added `"value": "{\"jsonrpc\":\"2.0\",\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2025-11-25\",\"capabilities\":{}},\"id\":1}"` to the body object
- This contains the actual JSON-RPC request with all required fields: `jsonrpc`, `method`, and `id`

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

## Root Cause Analysis
The server already has code to handle the Llama.cpp envelope format (`handle_envelope_envelope` and `EnvelopeMiddleware`), but the middleware wasn't being applied to the FastMCP application. This meant that even though the envelope format was detected and could be extracted, the extraction wasn't happening because the middleware was never actually used.

## Solution
I've modified the `run_http_transport` function in `/Users/edwinhm/MCP-Youtube/src/mcp_youtube/mcp_server.py` to:

1. Access the internal Starlette app created by FastMCP
2. Add the `EnvelopeMiddleware` to the Starlette app
3. This ensures that incoming requests are intercepted and the envelope format is properly handled

## Testing the Fix

### Option 1: Restart the Server (Recommended)

To apply the code changes, restart the server on `192.168.1.121:9091`:

```bash
# SSH into the server and restart
ssh user@192.168.1.121
# Then restart the server process
```

After the server restarts, test with your original request:

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
      "size": 189
    },
    "jsonRpcMethods": ["initialize"]
  }
}'
```

The server should now properly extract the JSON-RPC request from the envelope format.

### Option 2: Use the Corrected Request (Temporary Workaround)

If you can't restart the server, use the corrected request with the `value` field:

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

## Files Modified

### `/Users/edwinhm/MCP-Youtube/src/mcp_youtube/mcp_server.py`

1. **Fixed EnvelopeMiddleware class** (lines ~173-221):
   - Removed the incorrect `wrapped_receive` function that was overriding the modified `receive` function
   - Now correctly passes the extracted JSON-RPC to the underlying app

2. **Updated run_http_transport function** (lines ~376-422):
   - Added logic to detect the FastMCP internal Starlette app
   - Added `EnvelopeMiddleware` to the Starlette app
   - Added error handling for cases where the app isn't available

3. **Simplified handle_mcp_request function** (lines ~83-116):
   - Removed the redundant envelope extraction logic
   - The middleware now handles this automatically

## How the Fix Works

1. When a request comes in, the `EnvelopeMiddleware` intercepts it
2. It reads the request body and checks if it's in Llama.cpp envelope format
3. If it's an envelope format, it extracts the JSON-RPC request from `body.value`
4. The middleware replaces the original request body with the extracted JSON-RPC
5. FastMCP processes the request as if it were a standard JSON-RPC request

## Verification

The existing tests in `/Users/edwinhm/MCP-Youtube/tests/test_envelope_handler.py` verify that the envelope extraction works correctly:

```bash
# Run the tests (after installing dependencies)
cd /Users/edwinhm/MCP-Youtube
pytest tests/test_envelope_handler.py -v
```

The tests verify:
- Envelope format with `value` field is correctly extracted
- Standard JSON-RPC format is passed through unchanged
- Invalid JSON in the envelope is handled gracefully