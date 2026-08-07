# MCP-Youtube
# (c)2026 - Dr. Edwin A. Hernandez
# MEVIA Project
#
A Modern Context Protocol (MCP) server for YouTube that retrieves and processes video content.a

## Features

- Retrieve YouTube video metadata (title, description, thumbnail)
- Extract and process video transcripts
- Generate video summaries
- Find similar videos
- Translate content to different languages
- Support for multiple transport methods: TCP, STDIO, and SSE

## Prerequisites

- Python 3.9+
- Google Cloud Project with YouTube Data API v3 enabled
- API key for YouTube Data API

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MCP-Youtube.git
cd MCP-Youtube
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your YouTube API key:
```
YOUTUBE_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # For translation and summarization
```

## Usage

### As an MCP Server

MCP-Youtube implements the Modern Context Protocol and can be used with LLMs that support MCP.

When an LLM encounters a YouTube URL (e.g., `http://youtube.com/watch?v=VIDEO_ID`), MCP-Youtube will:

1. Retrieve video metadata (title, description, thumbnail URL)
2. Extract the transcript
3. Generate a summary
4. Provide similar video recommendations
5. Support translation of content

### Transport Methods

MCP-Youtube supports multiple transport methods:

1. **TCP Transport**: Connect via TCP socket
2. **STDIO Transport**: Use standard input/output for communication
3. **SSE Transport**: Server-Sent Events for streaming communication

## API Endpoints

- `/youtube/video/{video_id}`: Get video metadata
- `/youtube/transcript/{video_id}`: Get video transcript
- `/youtube/summary/{video_id}`: Get video summary
- `/youtube/similar/{video_id}`: Get similar videos
- `/youtube/translate`: Translate content

## Configuration

Environment variables:
- `YOUTUBE_API_KEY`: Your YouTube Data API key (required)
- `OPENAI_API_KEY`: Your OpenAI API key for translation/summarization (optional)
- `MCP_PORT`: Port for TCP transport (default: 3000)
- `LOG_LEVEL`: Logging level (default: INFO)

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest tests/
```

3. Run the server:
```bash
python -m mcp_youtube
```

## License

MIT License
