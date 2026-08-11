# YouTube Thumbnail Processing Documentation

## Overview

This document describes the thumbnail processing functionality added to the MCP YouTube server. This feature enables retrieval of YouTube video thumbnails in multiple formats, specifically designed for LLM image processing.

## Features

### 1. PNG Format Conversion
- **Method**: `get_video_thumbnail_as_png(video_id, thumbnail_type="high")`
- **Purpose**: Converts YouTube thumbnails to PNG format for LLM image processing
- **Use Case**: Videos from TechedTV and similar sources that include thumbnail images

### 2. Flexible Format Selection
- **Method**: `get_video_thumbnail(video_id, thumbnail_type="high", return_format="bytes")`
- **Formats Supported**:
  - `bytes`: Raw image bytes (default)
  - `url`: Thumbnail URL string
  - `base64`: Base64 encoded image string
  - `png`: PNG format image bytes

### 3. MCP Tools

The following MCP tools are available:

#### `get_video_thumbnail_as_png`
Retrieves video thumbnail as PNG image bytes for LLM processing.

**Parameters**:
- `video_id` (str): YouTube video ID or URL
- `thumbnail_type` (str): Thumbnail resolution ('default', 'medium', 'high', 'standard', 'maxres')

**Returns**: PNG format image bytes or error dictionary

#### `get_video_thumbnail_url`
Retrieves video thumbnail as URL string.

**Parameters**:
- `video_id` (str): YouTube video ID or URL
- `thumbnail_type` (str): Thumbnail resolution ('default', 'medium', 'high', 'standard', 'maxres')

**Returns**: Thumbnail URL string or error dictionary

#### `get_video_details` (Enhanced)
Added `include_thumbnail` parameter:
- `url`: Thumbnail URL (default)
- `bytes`: Image bytes (placeholder in JSON)
- `base64`: Base64 encoded image
- `none`: No thumbnail included

## Usage Examples

### Python Example

```python
import asyncio
from mcp_youtube.youtube_client import YouTubeClient

async def main():
    client = YouTubeClient(api_key="YOUR_API_KEY")
    
    # Get thumbnail as PNG for LLM processing
    png_bytes = await client.get_video_thumbnail_as_png("dQw4w9WgXcQ")
    
    # Get thumbnail as URL
    url = await client.get_video_thumbnail_url("dQw4w9WgXcQ")
    
    # Get thumbnail as base64
    base64_image = await client.get_video_thumbnail(
        "dQw4w9WgXcQ", 
        return_format="base64"
    )

asyncio.run(main())
```

### MCP Tool Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_video_thumbnail_as_png",
    "arguments": {
      "video_id": "dQw4w9WgXcQ",
      "thumbnail_type": "high"
    }
  }
}
```

## Error Handling

The implementation includes comprehensive error handling:

- **Missing thumbnails**: Returns appropriate error message
- **PIL/Pillow not installed**: Returns informative error suggesting installation
- **Network errors**: Handles connection issues gracefully
- **Invalid video IDs**: Returns "Video not found" error

## Testing

All tests pass (36 passed, 1 skipped):

```
tests/test_youtube_client.py::TestPNGThumbnailConversion - 4 tests
tests/test_youtube_client.py::TestThumbnailFormatSelection - 4 tests
```

## Installation Requirements

### Optional Dependencies

For PNG conversion, PIL/Pillow is required:

```bash
pip install Pillow
```

If PIL is not installed, the implementation gracefully handles this with an informative error message.

## Implementation Details

### New Methods in YouTubeClient

1. **`convert_to_png(image_data: bytes) -> bytes`**
   - Converts any image format to PNG
   - Uses PIL/Pillow for conversion
   - Handles RGBA to RGB conversion for compatibility

2. **`get_video_thumbnail_as_png(video_id: str, thumbnail_type: str = "high") -> Union[Dict, bytes]`**
   - Gets thumbnail in original format
   - Converts to PNG format
   - Returns PNG bytes

3. **`get_video_thumbnail(video_id: str, thumbnail_type: str = "high", save_path: Optional[str] = None, return_format: str = "bytes") -> Union[Dict, bytes, str]`**
   - Flexible format selection
   - Supports 'bytes', 'url', and 'base64' formats

### MCP Server Integration

Three new MCP tools added:

1. `get_video_thumbnail_as_png` - PNG format for LLM processing
2. `get_video_thumbnail_url` - URL format for linking
3. `get_video_details` - Enhanced with thumbnail inclusion options

## Supported Thumbnail Types

- `default`: Standard resolution (120x90)
- `medium`: Medium resolution (320x180)
- `high`: High resolution (640x480) - default
- `standard`: Standard resolution (1280x720)
- `maxres`: Maximum resolution (1920x1080)

## Notes

- All videos from TechedTV include thumbnail images that can be retrieved
- For videos without thumbnail images, the system returns the URL format as fallback
- PNG conversion is performed automatically when using `get_video_thumbnail_as_png`
- The implementation is backward compatible with existing code

## Troubleshooting

### PIL/Pillow Error
If you see "PIL/Pillow is required for image conversion":
```bash
pip install Pillow
```

### Thumbnail Not Available
Some videos may not have all thumbnail resolutions available. Try:
- Using a different `thumbnail_type` parameter
- Checking if the video ID is correct
- Verifying API key has proper permissions
