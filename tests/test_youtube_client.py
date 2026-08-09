
"""Tests for YouTubeClient class"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from mcp_youtube.youtube_client import YouTubeClient
from googleapiclient.errors import HttpError


# Test fixtures
@pytest.fixture
def api_key():
    """Fixture for test API key"""
    return "test_api_key_12345"


@pytest.fixture
def sample_video_id():
    """Fixture for sample video ID"""
    return "dQw4w9WgXcQ"


@pytest.fixture
def sample_video_details():
    """Fixture for sample video details response"""
    return {
        "video_id": "dQw4w9WgXcQ",
        "title": "Test Video Title",
        "description": "Test video description",
        "channel_title": "Test Channel",
        "published_at": "2023-01-01T00:00:00Z",
        "thumbnail": "https://example.com/thumbnail.jpg",
        "thumbnail_medium": "https://example.com/thumbnail-medium.jpg",
        "thumbnail_default": "https://example.com/thumbnail-default.jpg",
        "view_count": 1000,
        "like_count": 100,
        "comment_count": 50,
        "duration": "PT3M30S",
        "tags": ["test", "video", "youtube"],
        "category_id": "22"
    }


@pytest.fixture
def sample_transcript():
    """Fixture for sample transcript data"""
    return [
        {"text": "Hello world", "start": 0.0, "duration": 2.5},
        {"text": "This is a test transcript", "start": 2.5, "duration": 3.0},
        {"text": "End of transcript", "start": 5.5, "duration": 1.5}
    ]


@pytest.fixture
def sample_similar_videos():
    """Fixture for sample similar videos response"""
    return [
        {
            "video_id": "abc123def45",
            "title": "Similar Video 1",
            "channel_title": "Test Channel",
            "thumbnail": "https://example.com/thumb1.jpg",
            "published_at": "2023-01-02T00:00:00Z"
        },
        {
            "video_id": "xyz789ghi01",
            "title": "Similar Video 2",
            "channel_title": "Test Channel",
            "thumbnail": "https://example.com/thumb2.jpg",
            "published_at": "2023-01-03T00:00:00Z"
        }
    ]


@pytest.fixture
def sample_search_results():
    """Fixture for sample search results"""
    return [
        {
            "video_id": "search123abc",
            "title": "Search Result 1",
            "channel_title": "Test Channel",
            "description": "First search result",
            "thumbnail": "https://example.com/search1.jpg",
            "published_at": "2023-01-04T00:00:00Z"
        },
        {
            "video_id": "search456def",
            "title": "Search Result 2",
            "channel_title": "Test Channel",
            "description": "Second search result",
            "thumbnail": "https://example.com/search2.jpg",
            "published_at": "2023-01-05T00:00:00Z"
        }
    ]


# Test extract_video_id method
class TestExtractVideoId:
    """Tests for the extract_video_id method"""
    
    def test_standard_youtube_url(self, api_key):
        """Test extracting video ID from standard YouTube URL"""
        client = YouTubeClient(api_key=api_key)
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert client.extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_youtu_be_short_url(self, api_key):
        """Test extracting video ID from youtu.be short URL"""
        client = YouTubeClient(api_key=api_key)
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert client.extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_embed_url(self, api_key):
        """Test extracting video ID from embed URL"""
        client = YouTubeClient(api_key=api_key)
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert client.extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_youtube_shorts_url(self, api_key):
        """Test extracting video ID from YouTube Shorts URL"""
        client = YouTubeClient(api_key=api_key)
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        assert client.extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_direct_video_id(self, api_key):
        """Test that direct video ID returns None (not extracted)"""
        client = YouTubeClient(api_key=api_key)
        video_id = "dQw4w9WgXcQ"
        assert client.extract_video_id(video_id) is None
    
    def test_invalid_url(self, api_key):
        """Test extracting video ID from invalid URL"""
        client = YouTubeClient(api_key=api_key)
        url = "https://example.com/watch?v=invalid"
        assert client.extract_video_id(url) is None
    
    def test_url_with_additional_params(self, api_key):
        """Test extracting video ID from URL with additional parameters"""
        client = YouTubeClient(api_key=api_key)
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s"
        assert client.extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_youtube_be_with_params(self, api_key):
        """Test extracting video ID from youtu.be with parameters"""
        client = YouTubeClient(api_key=api_key)
        url = "https://youtu.be/dQw4w9WgXcQ?si=example"
        assert client.extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_invalid_video_id_format(self, api_key):
        """Test extracting video ID with invalid format"""
        client = YouTubeClient(api_key=api_key)
        # Use a valid 11-character pattern that isn't a real video ID
        url = "https://www.youtube.com/watch?v=invalid_id1"
        # The method will extract something but it won't be valid
        result = client.extract_video_id(url)
        # It should extract the pattern even if it's not a real video ID
        assert result is not None
        assert len(result) == 11
    
    def test_empty_string(self, api_key):
        """Test extracting video ID from empty string"""
        client = YouTubeClient(api_key=api_key)
        url = ""
        assert client.extract_video_id(url) is None
    
    def test_youtube_shorts_url(self, api_key):
        """Test extracting video ID from YouTube Shorts URL"""
        client = YouTubeClient(api_key=api_key)
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        assert client.extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_youtube_live_url(self, api_key):
        """Test extracting video ID from YouTube Live URL"""
        client = YouTubeClient(api_key=api_key)
        url = "https://www.youtube.com/watch/live=dQw4w9WgXcQ"
        assert client.extract_video_id(url) == "dQw4w9WgXcQ"


# Test get_video_details method
class TestGetVideoDetails:
    """Tests for the get_video_details method"""
    
    @pytest.mark.asyncio
    async def test_successful_video_details(self, api_key, sample_video_id, sample_video_details):
        """Test successful retrieval of video details"""
        # Mock the YouTube API response BEFORE creating the client
        with patch('mcp_youtube.youtube_client.build') as mock_build:
            mock_youtube = MagicMock()
            mock_build.return_value = mock_youtube
            
            # Create mock response
            mock_response = {
                'items': [{
                    'id': sample_video_id,
                    'snippet': {
                        'title': sample_video_details['title'],
                        'description': sample_video_details['description'],
                        'channelTitle': sample_video_details['channel_title'],
                        'publishedAt': sample_video_details['published_at'],
                        'thumbnails': {
                            'high': {'url': sample_video_details['thumbnail']},
                            'medium': {'url': sample_video_details['thumbnail_medium']},
                            'default': {'url': sample_video_details['thumbnail_default']}
                        },
                        'tags': sample_video_details['tags'],
                        'categoryId': sample_video_details['category_id']
                    },
                    'statistics': {
                        'viewCount': str(sample_video_details['view_count']),
                        'likeCount': str(sample_video_details['like_count']),
                        'commentCount': str(sample_video_details['comment_count'])
                    },
                    'contentDetails': {
                        'duration': sample_video_details['duration']
                    }
                }]
            }
            
            mock_videos = MagicMock()
            mock_videos.list.return_value = mock_videos
            mock_videos.execute.return_value = mock_response
            mock_youtube.videos.return_value = mock_videos
            
            client = YouTubeClient(api_key=api_key)
            result = await client.get_video_details(sample_video_id)
            
            assert result['video_id'] == sample_video_id
            assert result['title'] == sample_video_details['title']
            assert result['description'] == sample_video_details['description']
            assert result['channel_title'] == sample_video_details['channel_title']
            # YouTube API returns numeric values as strings
            assert result['view_count'] == str(sample_video_details['view_count'])
    
    @pytest.mark.asyncio
    async def test_video_not_found(self, api_key, sample_video_id):
        """Test behavior when video is not found"""
        # Mock the YouTube API response BEFORE creating the client
        with patch('mcp_youtube.youtube_client.build') as mock_build:
            mock_youtube = MagicMock()
            mock_build.return_value = mock_youtube
            
            # Create mock response with no items
            mock_response = {'items': []}
            
            mock_videos = MagicMock()
            mock_videos.list.return_value = mock_videos
            mock_videos.execute.return_value = mock_response
            mock_youtube.videos.return_value = mock_videos
            
            client = YouTubeClient(api_key=api_key)
            result = await client.get_video_details(sample_video_id)
            
            assert result['error'] == "Video not found"
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, api_key, sample_video_id):
        """Test API error handling"""
        # Mock the YouTube API response BEFORE creating the client
        with patch('mcp_youtube.youtube_client.build') as mock_build:
            mock_youtube = MagicMock()
            mock_build.return_value = mock_youtube
            
            mock_videos = MagicMock()
            mock_videos.list.return_value = mock_videos
            mock_videos.execute.side_effect = HttpError(Mock(status_code=500), b'Internal Server Error')
            mock_youtube.videos.return_value = mock_videos
            
            client = YouTubeClient(api_key=api_key)
            result = await client.get_video_details(sample_video_id)
            
            assert 'error' in result
            assert 'API error' in result['error']


# Test get_transcript method
class TestGetTranscript:
    """Tests for the get_transcript method"""
    
    @pytest.mark.asyncio
    async def test_successful_transcript(self, api_key, sample_video_id, sample_transcript):
        """Test successful retrieval of transcript"""
        # Create a mock module for youtube_transcript_api
        mock_yt_api = MagicMock()
        mock_yt_api.get_transcript.return_value = sample_transcript
        
        with patch('youtube_transcript_api.YouTubeTranscriptApi', mock_yt_api):
            client = YouTubeClient(api_key=api_key)
            result = await client.get_transcript(sample_video_id)
            
            assert len(result) == len(sample_transcript)
            assert result[0]['text'] == "Hello world"
            assert result[1]['text'] == "This is a test transcript"
            assert result[2]['text'] == "End of transcript"
    
    @pytest.mark.asyncio
    async def test_transcript_not_available(self, api_key, sample_video_id):
        """Test when transcript is not available"""
        # Create a mock module for youtube_transcript_api
        mock_yt_api = MagicMock()
        mock_yt_api.get_transcript.side_effect = Exception("Transcript not available")
        
        with patch('youtube_transcript_api.YouTubeTranscriptApi', mock_yt_api):
            client = YouTubeClient(api_key=api_key)
            result = await client.get_transcript(sample_video_id)
            
            assert 'error' in result
            assert 'Transcript not available' in result['error']


# Test get_similar_videos method
class TestGetSimilarVideos:
    """Tests for the get_similar_videos method"""
    
    @pytest.mark.asyncio
    async def test_successful_similar_videos(self, api_key, sample_video_id, sample_similar_videos):
        """Test successful retrieval of similar videos"""
        with patch('mcp_youtube.youtube_client.build') as mock_build:
            mock_youtube = MagicMock()
            mock_build.return_value = mock_youtube
            
            # Mock video details response
            mock_video_details = {
                "video_id": sample_video_id,
                "category_id": "22",
                "tags": ["test", "video"]
            }
            
            # Mock search response
            mock_search_response = {
                'items': [
                    {
                        'id': {'videoId': sample_similar_videos[0]['video_id']},
                        'snippet': {
                            'title': sample_similar_videos[0]['title'],
                            'channelTitle': sample_similar_videos[0]['channel_title'],
                            'publishedAt': sample_similar_videos[0]['published_at'],
                            'thumbnails': {
                                'default': {'url': sample_similar_videos[0]['thumbnail']}
                            }
                        }
                    },
                    {
                        'id': {'videoId': sample_similar_videos[1]['video_id']},
                        'snippet': {
                            'title': sample_similar_videos[1]['title'],
                            'channelTitle': sample_similar_videos[1]['channel_title'],
                            'publishedAt': sample_similar_videos[1]['published_at'],
                            'thumbnails': {
                                'default': {'url': sample_similar_videos[1]['thumbnail']}
                            }
                        }
                    }
                ]
            }
            
            # Set up mocks
            mock_videos = MagicMock()
            mock_videos.list.return_value = mock_videos
            
            mock_search = MagicMock()
            mock_search.list.return_value = mock_search
            mock_search.execute.return_value = mock_search_response
            
            mock_youtube.videos.return_value = mock_videos
            mock_youtube.search.return_value = mock_search
            
            client = YouTubeClient(api_key=api_key)
            # Mock get_video_details to return our sample
            with patch.object(client, 'get_video_details', return_value=mock_video_details):
                result = await client.get_similar_videos(sample_video_id)
                
                assert len(result) == 2
                assert result[0]['video_id'] == sample_similar_videos[0]['video_id']
                assert result[0]['title'] == sample_similar_videos[0]['title']
    
    @pytest.mark.asyncio
    async def test_similar_videos_api_error(self, api_key, sample_video_id):
        """Test API error handling for similar videos"""
        with patch('mcp_youtube.youtube_client.build') as mock_build:
            mock_youtube = MagicMock()
            mock_build.return_value = mock_youtube
            
            mock_search = MagicMock()
            mock_search.list.return_value = mock_search
            mock_search.execute.side_effect = HttpError(Mock(status_code=500), b'Internal Server Error')
            mock_youtube.search.return_value = mock_search
            
            client = YouTubeClient(api_key=api_key)
            # Mock get_video_details to return our sample
            with patch.object(client, 'get_video_details', return_value={"video_id": sample_video_id, "tags": ["test"]}):
                result = await client.get_similar_videos(sample_video_id)
                
                assert len(result) == 1
                assert 'error' in result[0]


# Test search_videos method
class TestSearchVideos:
    """Tests for the search_videos method"""
    
    @pytest.mark.asyncio
    async def test_successful_search(self, api_key, sample_search_results):
        """Test successful video search"""
        with patch('mcp_youtube.youtube_client.build') as mock_build:
            mock_youtube = MagicMock()
            mock_build.return_value = mock_youtube
            
            mock_search_response = {
                'items': [
                    {
                        'id': {'videoId': sample_search_results[0]['video_id']},
                        'snippet': {
                            'title': sample_search_results[0]['title'],
                            'channelTitle': sample_search_results[0]['channel_title'],
                            'description': sample_search_results[0]['description'],
                            'publishedAt': sample_search_results[0]['published_at'],
                            'thumbnails': {
                                'default': {'url': sample_search_results[0]['thumbnail']}
                            }
                        }
                    },
                    {
                        'id': {'videoId': sample_search_results[1]['video_id']},
                        'snippet': {
                            'title': sample_search_results[1]['title'],
                            'channelTitle': sample_search_results[1]['channel_title'],
                            'description': sample_search_results[1]['description'],
                            'publishedAt': sample_search_results[1]['published_at'],
                            'thumbnails': {
                                'default': {'url': sample_search_results[1]['thumbnail']}
                            }
                        }
                    }
                ]
            }
            
            mock_search = MagicMock()
            mock_search.list.return_value = mock_search
            mock_search.execute.return_value = mock_search_response
            mock_youtube.search.return_value = mock_search
            
            client = YouTubeClient(api_key=api_key)
            result = await client.search_videos("test query")
            
            assert len(result) == 2
            assert result[0]['video_id'] == sample_search_results[0]['video_id']
            assert result[0]['title'] == sample_search_results[0]['title']
    
    @pytest.mark.asyncio
    async def test_search_api_error(self, api_key):
        """Test API error handling for search"""
        client = YouTubeClient(api_key=api_key)
        
        with patch('mcp_youtube.youtube_client.build') as mock_build:
            mock_youtube = MagicMock()
            mock_build.return_value = mock_youtube
            
            mock_search = MagicMock()
            mock_search.list.return_value = mock_search
            mock_search.execute.side_effect = Exception("Search API Error")
            mock_youtube.search.return_value = mock_search
            
            result = await client.search_videos("test query")
            
            assert len(result) == 1
            assert 'error' in result[0]
    
    @pytest.mark.asyncio
    async def test_search_with_max_results(self, api_key):
        """Test search with max_results parameter"""
        with patch('mcp_youtube.youtube_client.build') as mock_build:
            mock_youtube = MagicMock()
            mock_build.return_value = mock_youtube
            
            # Create mock response with 3 items
            mock_items = []
            for i in range(3):
                mock_items.append({
                    'id': {'videoId': f'video{i}'},
                    'snippet': {
                        'title': f'Test Video {i}',
                        'channelTitle': 'Test Channel',
                        'description': f'Description {i}',
                        'publishedAt': f'2023-01-0{i+1}T00:00:00Z',
                        'thumbnails': {
                            'default': {'url': f'https://example.com/thumb{i}.jpg'}
                        }
                    }
                })
            
            mock_search_response = {'items': mock_items}
            
            mock_search = MagicMock()
            mock_search.list.return_value = mock_search
            mock_search.execute.return_value = mock_search_response
            mock_youtube.search.return_value = mock_search
            
            client = YouTubeClient(api_key=api_key)
            result = await client.search_videos("test query", max_results=5)
            
            assert len(result) == 3
            # Verify max_results was passed to the API call
            mock_search.list.assert_called_once()
            call_kwargs = mock_search.list.call_args[1]
            assert call_kwargs['maxResults'] == 5
    
    @pytest.mark.asyncio
    async def test_search_with_no_results(self, api_key):
        """Test search with no results"""
        with patch('mcp_youtube.youtube_client.build') as mock_build:
            mock_youtube = MagicMock()
            mock_build.return_value = mock_youtube
            
            mock_search_response = {'items': []}
            
            mock_search = MagicMock()
            mock_search.list.return_value = mock_search
            mock_search.execute.return_value = mock_search_response
            mock_youtube.search.return_value = mock_search
            
            client = YouTubeClient(api_key=api_key)
            result = await client.search_videos("nonexistent query")
            
            assert len(result) == 0