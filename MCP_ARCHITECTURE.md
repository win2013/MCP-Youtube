
# MCP Module Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     MCP Server Layer                                       │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐                          │
│  │  HTTP Transport  │  │   SSE Transport  │  │  STDIO Transport │                          │
│  │  (Uvicorn)       │  │   (FastMCP)      │  │   (FastMCP)      │                          │
│  └────────┬─────────┘  └──────────────────┘  └──────────────────┘                          │
│           │                                                                                 │
│           └───────────────┬─────────────────┘                                               │
│                           │                                                                 │
│                   ┌───────▼────────┐                                                        │
│                   │  FastMCP App   │                                                        │
│                   │  (Core Server) │                                                        │
│                   └───────┬────────┘                                                        │
│                           │                                                                 │
│                  ┌────────▼────────┐                                                        │
│                  │  CORS Middleware│                                                        │
│                  │  (Starlette)    │                                                        │
│                  └────────┬────────┘                                                        │
│                           │                                                                 │
│                  ┌────────▼────────┐                                                        │
│                  │ Envelope Middleware│                                                     │
│                  │ (Llama.cpp compat)│                                                      │
│                  └────────┬────────┘                                                        │
│                           │                                                                 │
└───────────────────────────┼─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     Business Logic Layer                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌────────────────────────┐   │
│  │ get_video_details│ │ get_transcript │ │ get_similar     │ │  search_videos         │   │
│  │                 │ │                 │ │  videos         │ │                        │   │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘ └─────────┬──────────────┘   │
│           │                   │                   │                    │                   │
│           └───────────────────┼───────────────────┼────────────────────┘                   │
│                               │                   │                                         │
│                               ▼                   ▼                                         │
│                  ┌────────────────────────────────┐                                        │
│                  │    YouTubeClient Class         │                                        │
│                  │                                │                                        │
│                  │  - API Key Management          │                                        │
│                  │  - Video ID Extraction         │                                        │
│                  │  - Request Retry Logic         │                                        │
│                  └────────────────────────────────┘                                        │
│                               │                                                             │
└───────────────────────────────┼─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    External Services Layer                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐                  │
│  │  YouTube Data    │      │  YouTube           │      │  Google API      │                  │
│  │  API v3          │      │  Transcript API    │      │  Discovery       │                  │
│  │  (videos.list)   │      │  (transcripts)     │      │  (build client)  │                  │
│  └────────┬─────────┘      └──────────────────┘      └──────────────────┘                  │
│           │                                                                                 │
│           └───────────────────────────────────────────────────────────────────┘             │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Module Structure

```
mcp_youtube/
├── __init__.py          # Package exports and version
├── mcp_server.py        # Main MCP server implementation
│   ├── FastMCP instance
│   ├── CORS middleware
│   ├── Envelope middleware
│   ├── Transport functions (HTTP, SSE, STDIO)
│   └── Tool definitions (get_video_details, get_transcript, etc.)
│
└── youtube_client.py    # YouTube API client
    ├── YouTubeClient class
    ├── Video ID extraction
    ├── Video details retrieval
    ├── Transcript fetching
    ├── Similar videos search
    └── Video search functionality
```

## Request Flow

```
Client Request
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. HTTP Server (Uvicorn)                                    │
│    - Listens on 0.0.0.0:9090 (or MCP_PORT)                  │
└─────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. CORS Middleware                                          │
│    - Handles preflight OPTIONS requests                     │
│    - Sets Access-Control-Allow-Origin headers               │
│    - Allows specified headers (mcp-protocol-version, etc.)  │
└─────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Envelope Middleware (if Llama.cpp format)               │
│    - Detects Llama.cpp envelope format                      │
│    - Extracts JSON-RPC from body.value                      │
│    - Replaces request body with extracted JSON-RPC          │
└─────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. FastMCP Router                                           │
│    - Routes to appropriate tool based on method name        │
│    - Validates JSON-RPC parameters                          │
└─────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Tool Handler (e.g., get_video_details)                  │
│    - Gets YouTube client from pool                          │
│    - Extracts video ID from URL or plain ID                 │
└─────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. YouTubeClient                                            │
│    - Authenticates with YouTube Data API                    │
│    - Makes API requests                                     │
│    - Handles errors and rate limits                         │
└─────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. External YouTube APIs                                    │
│    - videos.list (metadata, stats, contentDetails)          │
│    - search.list (similar videos, search results)           │
│    - YouTube Transcript API (transcripts)                   │
└─────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. Response Serialization                                   │
│    - Formats response as JSON-RPC                           │
│    - Adds proper status codes                               │
│    - Returns to client                                      │
└─────────────────────────────────────────────────────────────┘
```

## Transport Methods

### 1. HTTP Transport (Streamable HTTP)
- Uses Uvicorn ASGI server
- Supports both JSON and SSE content types
- Handles long-lived and short-lived connections
- Default port: 9090

### 2. SSE Transport (Server-Sent Events)
- Uses FastMCP's built-in SSE implementation
- Real-time streaming of server events
- Single connection for multiple requests

### 3. STDIO Transport
- Uses standard input/output for communication
- Ideal for local processes and embedding
- No network overhead

## Configuration

### Environment Variables
```bash
YOUTUBE_API_KEY=your_youtube_api_key_here  # Required
MCP_PORT=9090                              # Default port
MCP_TOKEN_KEY=your_token_here              # Auto-generated if not set
LOG_LEVEL=INFO                             # Logging level
```

### Environment File
- `.env.example` - Template (committed to Git)
- `.env_yt` - Actual configuration (git-ignored)

## Key Components

### FastMCP Framework
- Provides MCP protocol implementation
- Handles JSON-RPC serialization/deserialization
- Supports multiple transport methods
- Tool registration and discovery

### CORS Middleware
- Enables cross-origin requests
- Allows Llama.cpp WebUI and other clients
- Configurable allowed origins and headers

### Envelope Middleware
- Handles Llama.cpp envelope format
- Extracts JSON-RPC from wrapped requests
- Ensures compatibility with various MCP clients

### YouTubeClient
- Centralized YouTube API interactions
- Video ID parsing from various URL formats
- Error handling and retry logic
- Client pooling for efficiency

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/mcp` | JSON-RPC requests for all tools |
| GET | `/mcp` | Health check (SSE transport) |

## Tools Available

1. **get_video_details(video_id)** - Get video metadata
2. **get_transcript(video_id)** - Get video transcript
3. **get_similar_videos(video_id, max_results=10)** - Find similar content
4. **search_videos(query, max_results=10)** - Search YouTube videos

## Error Handling

- YouTube API errors caught and returned as error objects
- Invalid video IDs handled gracefully
- Missing API keys raise ValueError
- Network timeouts handled by client libraries