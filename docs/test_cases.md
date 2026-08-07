
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