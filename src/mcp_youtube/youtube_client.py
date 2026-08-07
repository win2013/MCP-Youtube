"""YouTube API client for retrieving video information"""
"""Edwin A. Hernandez, PhD """

import argparse
import asyncio
import json
import importlib
import os
import re
from typing import Dict, List, Optional

try:
    from googleapiclient.discovery import build  # type: ignore
    from googleapiclient.errors import HttpError  # type: ignore
except ImportError as e:
    raise ImportError("Install google-api-python-client") from e


class YouTubeClient:
    """Client for interacting with YouTube Data API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize YouTube client
        
        Args:
            api_key: YouTube Data API key. If not provided, 
                    reads from YOUTUBE_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY environment variable.")
        
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL
        
        Args:
            url: YouTube URL (can be various formats)
            
        Returns:
            Video ID if found, None otherwise
        """
        # Various YouTube URL patterns
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})',
            r'embed\/([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def get_video_details(self, video_id: str) -> Dict:
        """Get detailed information about a YouTube video
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video details
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            
            if not response.get("items"):
                return {"error": "Video not found"}
            
            video = response["items"][0]
            snippet = video["snippet"]
            statistics = video.get("statistics", {})
            content_details = video.get("contentDetails", {})
            
            return {
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "thumbnail_medium": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                "thumbnail_default": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                "view_count": statistics.get("viewCount", 0),
                "like_count": statistics.get("likeCount", 0),
                "comment_count": statistics.get("commentCount", 0),
                "duration": content_details.get("duration", ""),
                "tags": snippet.get("tags", []),
                "category_id": snippet.get("categoryId", ""),
            }
        except HttpError as e:
            return {"error": f"API error: {str(e)}"}
    
    async def get_transcript(self, video_id: str) -> List[Dict]:
        """Get transcript for a YouTube video
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of transcript segments with text and timestamps
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            return [
                {
                    "text": segment.get("text", ""),
                    "start": segment.get("start", 0),
                    "duration": segment.get("duration", 0)
                }
                for segment in transcript
            ]
        except Exception as e:
            return {"error": f"Transcript not available: {str(e)}"}
    
    async def get_similar_videos(self, video_id: str, max_results: int = 5) -> List[Dict]:
        """Get similar videos to a given YouTube video
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of similar videos to return
            
        Returns:
            List of similar video details
        """
        try:
            # First get the video's category and tags
            video_details = await self.get_video_details(video_id)
            
            if "error" in video_details:
                return [video_details]
            
            category_id = video_details.get("category_id")
            tags = video_details.get("tags", [])
            
            # Build search query from tags or category
            search_query = tags[0] if tags else category_id
            
            request = self.youtube.search().list(
                part="snippet",
                type="video",
                related_to_video_id=video_id,
                max_results=max_results
            )
            
            response = request.execute()
            
            similar_videos = []
            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                similar_videos.append({
                    "video_id": item["id"]["videoId"],
                    "title": snippet.get("title", ""),
                    "channel_title": snippet.get("channelTitle", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                    "published_at": snippet.get("publishedAt", "")
                })
            
            return similar_videos
        except HttpError as e:
            return [{"error": f"API error: {str(e)}"}]
    
    async def search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for YouTube videos
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            
        Returns:
            List of video details matching the search
        """
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results
            )
            
            response = request.execute()
            
            videos = []
            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                videos.append({
                    "video_id": item["id"]["videoId"],
                    "title": snippet.get("title", ""),
                    "channel_title": snippet.get("channelTitle", ""),
                    "description": snippet.get("description", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                    "published_at": snippet.get("publishedAt", "")
                })
            
            return videos
        except HttpError as e:
            return [{"error": f"API error: {str(e)}"}]
    
    async def close(self):
        """Close HTTP client"""
        # No persistent async HTTP client is used by googleapiclient; nothing to close.
        return None


async def _run_client(args: argparse.Namespace) -> None:
    client = YouTubeClient(api_key=args.api_key)
    try:
        if args.command == "details":
            video_id = client.extract_video_id(args.video) or args.video
            result = await client.get_video_details(video_id)
        elif args.command == "transcript":
            video_id = client.extract_video_id(args.video) or args.video
            result = await client.get_transcript(video_id)
        elif args.command == "similar":
            video_id = client.extract_video_id(args.video) or args.video
            result = await client.get_similar_videos(video_id, max_results=args.max_results)
        elif args.command == "search":
            result = await client.search_videos(args.query, max_results=args.max_results)
        else:
            raise ValueError(f"Unknown command: {args.command}")

        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        await client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run YouTubeClient from the command line")
    parser.add_argument("--api-key", help="YouTube Data API key")
    subparsers = parser.add_subparsers(dest="command", required=True)

    details = subparsers.add_parser("details", help="Get details for a video")
    details.add_argument("video", help="YouTube video URL or ID")

    transcript = subparsers.add_parser("transcript", help="Get transcript for a video")
    transcript.add_argument("video", help="YouTube video URL or ID")

    similar = subparsers.add_parser("similar", help="Get similar videos")
    similar.add_argument("video", help="YouTube video URL or ID")
    similar.add_argument("--max-results", type=int, default=5, help="Number of similar videos to return")

    search = subparsers.add_parser("search", help="Search YouTube videos")
    search.add_argument("query", help="Search query")
    search.add_argument("--max-results", type=int, default=10, help="Maximum number of results")

    args = parser.parse_args()
    asyncio.run(_run_client(args))


if __name__ == "__main__":
    main()
