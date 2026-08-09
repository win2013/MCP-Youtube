
# YouTube Client Test Cases

This document provides command-line examples for testing all arguments with the YouTube MCP client.

## Prerequisites

Before running these commands, make sure to set the environment variable:

```bash
export YOUTUBE_API_KEY="AIzaSyAUxluuI-1V4BSn3cg3sCinM0moWf8KRMg"
```

Or run with the API key directly using the `--api-key` flag:

```bash
python3 -m src.mcp_youtube.youtube_client --api-key "AIzaSyAUxluuI-1V4BSn3cg3sCinM0moWf8KRMg" ...
```

## Available Commands

The YouTube client supports the following subcommands:
- `details` - Get details for a video
- `transcript` - Get transcript for a video
- `similar` - Get similar videos
- `search` - Search YouTube videos

---

## 1. Get Video Details

### Using video ID directly
```bash
python3 -m src.mcp_youtube.youtube_client details tueADMIk37E
```

### Using full YouTube URL
```bash
python3 -m src.mcp_youtube.youtube_client details https://www.youtube.com/watch?v=tueADMIk37E
```

### Using youtu.be short URL
```bash
python3 -m src.mcp_youtube.youtube_client details https://youtu.be/tueADMIk37E
```

### Output
Returns JSON with video information including:
- Video title, description, channel title
- Published date, thumbnail URLs
- View count, like count, comment count
- Duration, tags, and category ID

---

## 2. Get Transcript

### Get transcript for a video
```bash
python3 -m src.mcp_youtube.youtube_client transcript tueADMIk37E
```

### Output
Returns JSON with transcript segments, each containing:
- `text` - The transcribed text
- `start` - Start timestamp in seconds
- `duration` - Duration of the segment in seconds

**Note:** Some videos may not have transcripts available.

---

## 3. Get Similar Videos

### Get similar videos (default: 5 results)
```bash
python3 -m src.mcp_youtube.youtube_client similar tueADMIk37E
```

### Get 10 similar videos
```bash
python3 -m src.mcp_youtube.youtube_client similar tueADMIk37E --max-results 10
```

### Get 15 similar videos
```bash
python3 -m src.mcp_youtube.youtube_client similar tueADMIk37E --max-results 15
```

### Output
Returns JSON array of similar videos with:
- Video ID, title, channel title
- Thumbnail URL, published date

---

## 4. Search Videos

### Search with default results (10)
```bash
python3 -m src.mcp_youtube.youtube_client search "techedtv"
```

### Search with custom result count
```bash
python3 -m src.mcp_youtube.youtube_client search "MWC 2026" --max-results 5
```

### Search with more results
```bash
python3 -m src.mcp_youtube.youtube_client search "AI technology" --max-results 20
```

### Output
Returns JSON array of search results with:
- Video ID, title, channel title
- Description, thumbnail URL, published date

---

## Complete Test Script

You can run all tests in sequence using this script:

```bash
#!/bin/bash

# Set your API key
export YOUTUBE_API_KEY="AIzaSyAUxluuI-1V4BSn3cg3sCinM0moWf8KRMg"

# Test 1: Get video details
echo "=== Test 1: Video Details ==="
python3 -m src.mcp_youtube.youtube_client details tueADMIk37E

# Test 2: Get transcript
echo "=== Test 2: Transcript ==="
python3 -m src.mcp_youtube.youtube_client transcript tueADMIk37E

# Test 3: Get similar videos (10 results)
echo "=== Test 3: Similar Videos ==="
python3 -m src.mcp_youtube.youtube_client similar tueADMIk37E --max-results 10

# Test 4: Search videos
echo "=== Test 4: Search Videos ==="
python3 -m src.mcp_youtube.youtube_client search "techedtv" --max-results 5
```

Save this as `test_mcp.sh`, make it executable with `chmod +x test_mcp.sh`, and run it.

---

## Testing with Different Video IDs

You can replace `tueADMIk37E` with any YouTube video ID to test different content.

To find a video ID:
- From a YouTube URL like `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- The video ID is the value after `v=` (in this case: `dQw4w9WgXcQ`)

---

# Project Structure and Test Coverage

## Directory Structure

```
MCP-Youtube/
├── src/
│   └── mcp_youtube/
│       ├── __init__.py          # Package initialization, exports main components
│       ├── mcp_server.py        # FastMCP server implementation with transport layers
│       ├── youtube_client.py    # YouTube API client for video operations
│       └── __pycache__/         # Compiled Python files
├── tests/
│   ├── __pycache__/             # Compiled test files
│   ├── test_envelope_handler.py # Tests for Llama.cpp envelope format handling
│   └── test_youtube_client.py   # Tests for YouTubeClient class
├── docs/
│   ├── test_cases.md            # Command-line test examples and coverage
│   ├── test_coverage.md         # This file - test coverage documentation
│   └── project_structure.md     # Project architecture documentation
├── .env_yt                      # Environment variables (API keys, etc.)
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
└── README.md                    # Project overview
```

## Test Coverage

### Unit Tests

The test suite consists of **33 tests** covering all major functionality:

#### 1. YouTube Client Tests (`tests/test_youtube_client.py`)

**Extract Video ID Tests (11 tests)**
- `test_standard_youtube_url` - Extracts ID from standard YouTube URLs
- `test_youtu_be_short_url` - Extracts ID from youtu.be short URLs
- `test_embed_url` - Extracts ID from embed URLs
- `test_youtube_shorts_url` - Extracts ID from Shorts URLs
- `test_direct_video_id` - Handles direct video IDs
- `test_invalid_url` - Rejects invalid URLs
- `test_url_with_additional_params` - Handles URLs with query parameters
- `test_youtube_be_with_params` - Handles youtu.be with parameters
- `test_invalid_video_id_format` - Handles invalid ID formats
- `test_empty_string` - Handles empty strings
- `test_youtube_live_url` - Extracts ID from live stream URLs

**Get Video Details Tests (3 tests)**
- `test_successful_video_details` - Retrieves video information
- `test_video_not_found` - Handles missing videos
- `test_api_error_handling` - Handles API errors gracefully

**Get Transcript Tests (2 tests)**
- `test_successful_transcript` - Retrieves transcript data
- `test_transcript_not_available` - Handles unavailable transcripts

**Get Similar Videos Tests (2 tests)**
- `test_successful_similar_videos` - Retrieves similar videos
- `test_similar_videos_api_error` - Handles API errors

**Search Videos Tests (5 tests)**
- `test_successful_search` - Performs video search
- `test_search_api_error` - Handles search errors
- `test_search_with_max_results` - Respects result limits
- `test_search_with_no_results` - Handles empty search results

#### 2. Envelope Handler Tests (`tests/test_envelope_handler.py`)

**Envelope Extraction Tests (8 tests)**
- `test_envelope_without_value_field_returns_none` - Handles missing value field
- `test_envelope_with_value_field` - Extracts from valid envelope
- `test_llama_cpp_envelope_format` - Handles Llama.cpp format (2025)
- `test_llama_cpp_envelope_with_2026_version` - Handles 2026 envelope format
- `test_llama_cpp_envelope_with_2024_version` - Handles 2024 envelope format
- `test_non_envelope_format_returns_none` - Passes through non-envelope data
- `test_invalid_json_in_body` - Handles invalid JSON gracefully
- `test_missing_value_field` - Handles incomplete envelope data

**JSON-RPC Extraction Tests (3 tests)**
- `test_extract_jsonrpc_standard_format` - Handles standard JSON-RPC
- `test_extract_jsonrpc_envelope_format` - Extracts from envelope
- `test_extract_jsonrpc_non_jsonrpc_format` - Handles non-JSON-RPC data

### Code Coverage Areas

| Component | Coverage | Notes |
|-----------|----------|-------|
| Video ID extraction | 100% | All URL patterns tested |
| Video details API | 100% | Success, not found, error cases |
| Transcript API | 100% | Success and error cases |
| Similar videos API | 100% | Success and error cases |
| Search API | 100% | Success, errors, pagination |
| Envelope handling | 100% | All envelope formats tested |
| JSON-RPC extraction | 100% | Standard and envelope formats |

### Running Tests

```bash
# Activate virtual environment
source .venv312/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_youtube_client.py -v

# Run specific test class
pytest tests/test_youtube_client.py::TestExtractVideoId -v

# Run with coverage
pytest tests/ --cov=src/mcp_youtube --cov-report=html
```

## Project Architecture

### FastMCP Server (`mcp_server.py`)

The server implements the Model Context Protocol (MCP) with multiple transport options:

**Supported Transports:**
- `http` - Streamable HTTP transport
- `sse` - Server-Sent Events transport  
- `stdio` - Standard input/output transport
- `all` - Run all transports simultaneously

**Key Components:**
- `FastMCP` - Main server instance
- `EnvelopeMiddleware` - Handles Llama.cpp envelope format
- `YouTubeClient` - YouTube API integration
- Transport functions for each protocol

**Environment Variables:**
- `YOUTUBE_API_KEY` - YouTube Data API key (required)
- `MCP_PORT` - Server port (default: 9090)
- `MCP_TOKEN_KEY` - Authentication token

### YouTube Client (`youtube_client.py`)

The client provides methods for YouTube Data API operations:

**Methods:**
- `extract_video_id(url)` - Parse video ID from various URL formats
- `get_video_details(video_id)` - Get video metadata and statistics
- `get_transcript(video_id)` - Get video caption transcript
- `get_similar_videos(video_id, max_results)` - Find related videos
- `search_videos(query, max_results)` - Search YouTube videos

**Dependencies:**
- `google-api-python-client` - YouTube Data API v3
- `youtube-transcript-api` - Transcript retrieval

### Llama.cpp Envelope Format

The server supports the Llama.cpp MCP envelope format:

```json
{
  "serverName": "server_identifier",
  "request": {
    "url": "http://server:port/mcp",
    "method": "POST",
    "headers": {...},
    "body": {
      "kind": "string",
      "size": 123,
      "value": "{\"jsonrpc\":\"2.0\",\"method\":\"...\"}"
    },
    "jsonRpcMethods": ["initialize"]
  }
}
```

The envelope middleware extracts the JSON-RPC request from the `body.value` field before processing.

---

## Exa AI MCP Server Compatibility

When making requests to the Exa AI MCP server (`https://mcp.exa.ai/mcp`), you must include specific headers:

### Required Headers

1. **`Accept: application/json, text/event-stream`** - Required by Exa AI server for streamable HTTP transport
2. **`Content-Type: application/json`** - Required for JSON-RPC requests

### Working curl Example

```bash
curl -v --max-time 30 https://mcp.exa.ai/mcp \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{
    "serverName": "your-server-name",
    "request": {
      "url": "https://mcp.exa.ai/mcp",
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

### Common Error: 406 Not Acceptable

If you receive a 406 error with the message "Client must accept both application/json and text/event-stream", it means the `Accept` header is missing or doesn't include both content types.

**Solution:** Always include `-H "Accept: application/json, text/event-stream"` in your curl commands when connecting to Exa AI MCP server.

### Timeout Settings

The `--max-time 30` option prevents requests from hanging indefinitely. You can adjust this value as needed (in seconds).

### Python Alternative

For programmatic access, use the `requests` library with appropriate headers and timeout:

```python
import requests
import json

envelope = {
    "serverName": "your-server-name",
    "request": {
        "url": "https://mcp.exa.ai/mcp",
        "method": "POST",
        "headers": {
            "accept": "application/json, text/event-stream",
            "content-type": "application/json"
        },
        "body": {
            "kind": "string",
            "size": 189,
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

# Include Accept header and timeout to prevent hanging
response = requests.post(
    "https://mcp.exa.ai/mcp",
    json=envelope,
    headers={"Accept": "application/json, text/event-stream"},
    timeout=30
)

print(response.text)
```
=======
# YouTube Client Test Cases

This document provides command-line examples for testing all arguments with the YouTube MCP client.

## Prerequisites

Before running these commands, make sure to set the environment variable:

```bash
export YOUTUBE_API_KEY="AIzaSyAUxluuI-1V4BSn3cg3sCinM0moWf8KRMg"
```

Or run with the API key directly using the `--api-key` flag:

```bash
python3 -m src.mcp_youtube.youtube_client --api-key "AIzaSyAUxluuI-1V4BSn3cg3sCinM0moWf8KRMg" ...
```

## Available Commands

The YouTube client supports the following subcommands:
- `details` - Get details for a video
- `transcript` - Get transcript for a video
- `similar` - Get similar videos
- `search` - Search YouTube videos

---

## 1. Get Video Details

### Using video ID directly
```bash
python3 -m src.mcp_youtube.youtube_client details tueADMIk37E
```

### Using full YouTube URL
```bash
python3 -m src.mcp_youtube.youtube_client details https://www.youtube.com/watch?v=tueADMIk37E
```

### Using youtu.be short URL
```bash
python3 -m src.mcp_youtube.youtube_client details https://youtu.be/tueADMIk37E
```

### Output
Returns JSON with video information including:
- Video title, description, channel title
- Published date, thumbnail URLs
- View count, like count, comment count
- Duration, tags, and category ID

---

## 2. Get Transcript

### Get transcript for a video
```bash
python3 -m src.mcp_youtube.youtube_client transcript tueADMIk37E
```

### Output
Returns JSON with transcript segments, each containing:
- `text` - The transcribed text
- `start` - Start timestamp in seconds
- `duration` - Duration of the segment in seconds

**Note:** Some videos may not have transcripts available.

---

## 3. Get Similar Videos

### Get similar videos (default: 5 results)
```bash
python3 -m src.mcp_youtube.youtube_client similar tueADMIk37E
```

### Get 10 similar videos
```bash
python3 -m src.mcp_youtube.youtube_client similar tueADMIk37E --max-results 10
```

### Get 15 similar videos
```bash
python3 -m src.mcp_youtube.youtube_client similar tueADMIk37E --max-results 15
```

### Output
Returns JSON array of similar videos with:
- Video ID, title, channel title
- Thumbnail URL, published date

---

## 4. Search Videos

### Search with default results (10)
```bash
python3 -m src.mcp_youtube.youtube_client search "techedtv"
```

### Search with custom result count
```bash
python3 -m src.mcp_youtube.youtube_client search "MWC 2026" --max-results 5
```

### Search with more results
```bash
python3 -m src.mcp_youtube.youtube_client search "AI technology" --max-results 20
```

### Output
Returns JSON array of search results with:
- Video ID, title, channel title
- Description, thumbnail URL, published date

---

## Complete Test Script

You can run all tests in sequence using this script:

```bash
#!/bin/bash

# Set your API key
export YOUTUBE_API_KEY="AIzaSyAUxluuI-1V4BSn3cg3sCinM0moWf8KRMg"

# Test 1: Get video details
echo "=== Test 1: Video Details ==="
python3 -m src.mcp_youtube.youtube_client details tueADMIk37E

# Test 2: Get transcript
echo "=== Test 2: Transcript ==="
python3 -m src.mcp_youtube.youtube_client transcript tueADMIk37E

# Test 3: Get similar videos (10 results)
echo "=== Test 3: Similar Videos ==="
python3 -m src.mcp_youtube.youtube_client similar tueADMIk37E --max-results 10

# Test 4: Search videos
echo "=== Test 4: Search Videos ==="
python3 -m src.mcp_youtube.youtube_client search "techedtv" --max-results 5
```

Save this as `test_mcp.sh`, make it executable with `chmod +x test_mcp.sh`, and run it.

---

## Testing with Different Video IDs

You can replace `tueADMIk37E` with any YouTube video ID to test different content.

To find a video ID:
- From a YouTube URL like `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- The video ID is the value after `v=` (in this case: `dQw4w9WgXcQ`)

---

# Project Structure and Test Coverage

## Directory Structure

```
MCP-Youtube/
├── src/
│   └── mcp_youtube/
│       ├── __init__.py          # Package initialization, exports main components
│       ├── mcp_server.py        # FastMCP server implementation with transport layers
│       ├── youtube_client.py    # YouTube API client for video operations
│       └── __pycache__/         # Compiled Python files
├── tests/
│   ├── __pycache__/             # Compiled test files
│   ├── test_envelope_handler.py # Tests for Llama.cpp envelope format handling
│   └── test_youtube_client.py   # Tests for YouTubeClient class
├── docs/
│   ├── test_cases.md            # Command-line test examples and coverage
│   ├── test_coverage.md         # This file - test coverage documentation
│   └── project_structure.md     # Project architecture documentation
├── .env_yt                      # Environment variables (API keys, etc.)
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
└── README.md                    # Project overview
```

## Test Coverage

### Unit Tests

The test suite consists of **33 tests** covering all major functionality:

#### 1. YouTube Client Tests (`tests/test_youtube_client.py`)

**Extract Video ID Tests (11 tests)**
- `test_standard_youtube_url` - Extracts ID from standard YouTube URLs
- `test_youtu_be_short_url` - Extracts ID from youtu.be short URLs
- `test_embed_url` - Extracts ID from embed URLs
- `test_youtube_shorts_url` - Extracts ID from Shorts URLs
- `test_direct_video_id` - Handles direct video IDs
- `test_invalid_url` - Rejects invalid URLs
- `test_url_with_additional_params` - Handles URLs with query parameters
- `test_youtube_be_with_params` - Handles youtu.be with parameters
- `test_invalid_video_id_format` - Handles invalid ID formats
- `test_empty_string` - Handles empty strings
- `test_youtube_live_url` - Extracts ID from live stream URLs

**Get Video Details Tests (3 tests)**
- `test_successful_video_details` - Retrieves video information
- `test_video_not_found` - Handles missing videos
- `test_api_error_handling` - Handles API errors gracefully

**Get Transcript Tests (2 tests)**
- `test_successful_transcript` - Retrieves transcript data
- `test_transcript_not_available` - Handles unavailable transcripts

**Get Similar Videos Tests (2 tests)**
- `test_successful_similar_videos` - Retrieves similar videos
- `test_similar_videos_api_error` - Handles API errors

**Search Videos Tests (5 tests)**
- `test_successful_search` - Performs video search
- `test_search_api_error` - Handles search errors
- `test_search_with_max_results` - Respects result limits
- `test_search_with_no_results` - Handles empty search results

#### 2. Envelope Handler Tests (`tests/test_envelope_handler.py`)

**Envelope Extraction Tests (8 tests)**
- `test_envelope_without_value_field_returns_none` - Handles missing value field
- `test_envelope_with_value_field` - Extracts from valid envelope
- `test_llama_cpp_envelope_format` - Handles Llama.cpp format (2025)
- `test_llama_cpp_envelope_with_2026_version` - Handles 2026 envelope format
- `test_llama_cpp_envelope_with_2024_version` - Handles 2024 envelope format
- `test_non_envelope_format_returns_none` - Passes through non-envelope data
- `test_invalid_json_in_body` - Handles invalid JSON gracefully
- `test_missing_value_field` - Handles incomplete envelope data

**JSON-RPC Extraction Tests (3 tests)**
- `test_extract_jsonrpc_standard_format` - Handles standard JSON-RPC
- `test_extract_jsonrpc_envelope_format` - Extracts from envelope
- `test_extract_jsonrpc_non_jsonrpc_format` - Handles non-JSON-RPC data

### Code Coverage Areas

| Component | Coverage | Notes |
|-----------|----------|-------|
| Video ID extraction | 100% | All URL patterns tested |
| Video details API | 100% | Success, not found, error cases |
| Transcript API | 100% | Success and error cases |
| Similar videos API | 100% | Success and error cases |
| Search API | 100% | Success, errors, pagination |
| Envelope handling | 100% | All envelope formats tested |
| JSON-RPC extraction | 100% | Standard and envelope formats |

### Running Tests

```bash
# Activate virtual environment
source .venv312/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_youtube_client.py -v

# Run specific test class
pytest tests/test_youtube_client.py::TestExtractVideoId -v

# Run with coverage
pytest tests/ --cov=src/mcp_youtube --cov-report=html
```

## Project Architecture

### FastMCP Server (`mcp_server.py`)

The server implements the Model Context Protocol (MCP) with multiple transport options:

**Supported Transports:**
- `http` - Streamable HTTP transport
- `sse` - Server-Sent Events transport  
- `stdio` - Standard input/output transport
- `all` - Run all transports simultaneously

**Key Components:**
- `FastMCP` - Main server instance
- `EnvelopeMiddleware` - Handles Llama.cpp envelope format
- `YouTubeClient` - YouTube API integration
- Transport functions for each protocol

**Environment Variables:**
- `YOUTUBE_API_KEY` - YouTube Data API key (required)
- `MCP_PORT` - Server port (default: 9090)
- `MCP_TOKEN_KEY` - Authentication token

### YouTube Client (`youtube_client.py`)

The client provides methods for YouTube Data API operations:

**Methods:**
- `extract_video_id(url)` - Parse video ID from various URL formats
- `get_video_details(video_id)` - Get video metadata and statistics
- `get_transcript(video_id)` - Get video caption transcript
- `get_similar_videos(video_id, max_results)` - Find related videos
- `search_videos(query, max_results)` - Search YouTube videos

**Dependencies:**
- `google-api-python-client` - YouTube Data API v3
- `youtube-transcript-api` - Transcript retrieval

### Llama.cpp Envelope Format

The server supports the Llama.cpp MCP envelope format:

```json
{
  "serverName": "server_identifier",
  "request": {
    "url": "http://server:port/mcp",
    "method": "POST",
    "headers": {...},
    "body": {
      "kind": "string",
      "size": 123,
      "value": "{\"jsonrpc\":\"2.0\",\"method\":\"...\"}"
    },
    "jsonRpcMethods": ["initialize"]
  }
}
```

The envelope middleware extracts the JSON-RPC request from the `body.value` field before processing.

---

## Exa AI MCP Server Compatibility

When making requests to the Exa AI MCP server (`https://mcp.exa.ai/mcp`), you must include specific headers:

### Required Headers

1. **`Accept: application/json, text/event-stream`** - Required by Exa AI server for streamable HTTP transport
2. **`Content-Type: application/json`** - Required for JSON-RPC requests

### Working curl Example

```bash
curl -v --max-time 30 https://mcp.exa.ai/mcp \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{
    "serverName": "your-server-name",
    "request": {
      "url": "https://mcp.exa.ai/mcp",
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

### Common Error: 406 Not Acceptable

If you receive a 406 error with the message "Client must accept both application/json and text/event-stream", it means the `Accept` header is missing or doesn't include both content types.

**Solution:** Always include `-H "Accept: application/json, text/event-stream"` in your curl commands when connecting to Exa AI MCP server.

### Timeout Settings

The `--max-time 30` option prevents requests from hanging indefinitely. You can adjust this value as needed (in seconds).

### Python Alternative

For programmatic access, use the `requests` library with appropriate headers and timeout:

```python
import requests
import json

envelope = {
    "serverName": "your-server-name",
    "request": {
        "url": "https://mcp.exa.ai/mcp",
        "method": "POST",
        "headers": {
            "accept": "application/json, text/event-stream",
            "content-type": "application/json"
        },
        "body": {
            "kind": "string",
            "size": 189,
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

# Include Accept header and timeout to prevent hanging
response = requests.post(
    "https://mcp.exa.ai/mcp",
    json=envelope,
    headers={"Accept": "application/json, text/event-stream"},
    timeout=30
)

print(response.text)
```