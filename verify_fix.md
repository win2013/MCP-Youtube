
# How to Verify the Fix

## Problem
The server running on `192.168.1.121:9090` is still using the old code. The code changes have been made locally but need to be deployed and the server restarted.

## Solution

### 1. Restart the Server

SSH into the server and restart the MCP server:

```bash
ssh user@192.168.1.121
# Find the process running on port 9090
lsof -i :9090
# Kill the process
kill <PID>
# Or use systemctl if it's a service
sudo systemctl restart mcp-server
```

### 2. Deploy the Updated Code

If you need to deploy the updated code first:

```bash
# From your local machine, copy the updated files
scp src/mcp_youtube/mcp_server.py user@192.168.1.121:/path/to/MCP-Youtube/src/mcp_youtube/

# Or use git if the server has access to the repo
ssh user@192.168.1.121
cd /path/to/MCP-Youtube
git pull origin main
```

### 3. Test After Restart

**Important:** For Exa AI MCP server compatibility and to prevent hanging requests:

- Include `--max-time 30` to prevent hanging requests
- Include `Accept: application/json, text/event-stream` header (required by Exa AI MCP server)

```bash
curl -v --max-time 30 http://192.168.1.121:9090/mcp \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{
  "serverName": "nu5vkp0km3",
  "request": {
    "url": "http://192.168.1.121:9090/mcp",
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

## What Was Fixed

### Code Changes Made

1. **Fixed EnvelopeMiddleware class** (`src/mcp_youtube/mcp_server.py`):
   - Removed the `wrapped_receive` function that was overriding the modified `receive` function
   - Now correctly passes the extracted JSON-RPC to the underlying app

2. **Updated run_http_transport function**:
   - Added logic to detect the FastMCP internal Starlette app
   - Added `EnvelopeMiddleware` to the Starlette app before starting

3. **Simplified handle_mcp_request function**:
   - Removed redundant envelope extraction logic

### How the Fix Works

1. When a request comes in, the `EnvelopeMiddleware` intercepts it
2. It reads the request body and checks if it's in Llama.cpp envelope format
3. If it's an envelope format, it extracts the JSON-RPC request
4. The middleware replaces the original request body with the extracted JSON-RPC
5. FastMCP processes the request as if it were a standard JSON-RPC request