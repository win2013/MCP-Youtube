curl -m 5  -X POST -v http://192.168.1.125:9091/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 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" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "curl-test",
        "version": "1.0"
      }
    }
  }'

