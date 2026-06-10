"""YouTube Data Source - Transcripts and video metadata."""
import asyncio
from datetime import datetime
from typing import AsyncIterator
import httpx
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from config import YOUTUBE_API_KEY, YOUTUBE_CHANNELS, YOUTUBE_SEARCH_TERMS
from .base import BaseSource, ContentItem


class YouTubeSource(BaseSource):
    """Fetch YouTube video transcripts and metadata."""
    
    name = "youtube"
    
    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    async def is_configured(self) -> bool:
        """Check if YouTube API is configured."""
        return bool(self.api_key)
    
    async def fetch(self, limit: int = 50) -> AsyncIterator[ContentItem]:
        """Fetch recent videos from channels and search results."""
        if not await self.is_configured():
            print("YouTube API not configured, skipping")
            return
        
        video_ids = set()
        
        # Get videos from channels
        async with httpx.AsyncClient() as client:
            for channel_id in YOUTUBE_CHANNELS[:5]:  # Limit channels per run
                try:
                    channel_videos = await self._get_channel_videos(client, channel_id, limit=5)
                    video_ids.update(channel_videos)
                except Exception as e:
                    print(f"Error fetching channel {channel_id}: {e}")
                await asyncio.sleep(0.5)  # Rate limiting
            
            # Get videos from search
            for query in YOUTUBE_SEARCH_TERMS[:5]:  # Limit searches per run
                try:
                    search_videos = await self._search_videos(client, query, limit=3)
                    video_ids.update(search_videos)
                except Exception as e:
                    print(f"Error searching '{query}': {e}")
                await asyncio.sleep(0.5)
        
        # Fetch transcripts and yield content
        count = 0
        for video_id in list(video_ids)[:limit]:
            try:
                content = await self._get_video_content(video_id)
                if content:
                    yield content
                    count += 1
                    if count >= limit:
                        break
            except Exception as e:
                print(f"Error processing video {video_id}: {e}")
            await asyncio.sleep(0.2)
    
    async def _get_channel_videos(self, client: httpx.AsyncClient, channel_id: str, limit: int = 10) -> list[str]:
        """Get recent video IDs from a channel."""
        # First get the uploads playlist ID
        response = await client.get(
            f"{self.base_url}/channels",
            params={
                "key": self.api_key,
                "id": channel_id,
                "part": "contentDetails",
            }
        )
        data = response.json()
        
        if not data.get("items"):
            return []
        
        uploads_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Get videos from uploads playlist
        response = await client.get(
            f"{self.base_url}/playlistItems",
            params={
                "key": self.api_key,
                "playlistId": uploads_id,
                "part": "contentDetails",
                "maxResults": limit,
            }
        )
        data = response.json()
        
        return [item["contentDetails"]["videoId"] for item in data.get("items", [])]
    
    async def _search_videos(self, client: httpx.AsyncClient, query: str, limit: int = 5) -> list[str]:
        """Search for videos matching a query."""
        response = await client.get(
            f"{self.base_url}/search",
            params={
                "key": self.api_key,
                "q": query,
                "type": "video",
                "part": "id",
                "maxResults": limit,
                "order": "date",
                "publishedAfter": "2024-01-01T00:00:00Z",
            }
        )
        data = response.json()
        
        return [item["id"]["videoId"] for item in data.get("items", [])]
    
    async def _get_video_content(self, video_id: str) -> ContentItem | None:
        """Get video metadata and transcript."""
        async with httpx.AsyncClient() as client:
            # Get video metadata
            response = await client.get(
                f"{self.base_url}/videos",
                params={
                    "key": self.api_key,
                    "id": video_id,
                    "part": "snippet,statistics",
                }
            )
            data = response.json()
            
            if not data.get("items"):
                return None
            
            video = data["items"][0]
            snippet = video["snippet"]
            stats = video.get("statistics", {})
            
            # Get transcript
            transcript_text = await self._get_transcript(video_id)
            if not transcript_text:
                # Fall back to description if no transcript
                transcript_text = snippet.get("description", "")[:2000]
            
            return ContentItem(
                source="youtube",
                source_id=video_id,
                title=snippet.get("title", ""),
                content=transcript_text,
                url=f"https://www.youtube.com/watch?v={video_id}",
                author=snippet.get("channelTitle", ""),
                engagement=int(stats.get("viewCount", 0)),
                published_at=datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")),
                metadata={
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "channel_id": snippet.get("channelId", ""),
                }
            )
    
    async def _get_transcript(self, video_id: str) -> str | None:
        """Get video transcript using youtube-transcript-api."""
        try:
            # Run in executor since youtube-transcript-api is synchronous
            loop = asyncio.get_event_loop()
            
            def fetch_transcript():
                # youtube-transcript-api v0.6+ uses instance methods
                ytt_api = YouTubeTranscriptApi()
                transcript_list = ytt_api.fetch(video_id)
                return transcript_list
            
            transcript_list = await loop.run_in_executor(None, fetch_transcript)
            
            # Combine transcript segments
            full_text = " ".join([segment.text for segment in transcript_list])
            
            # Limit to ~5000 chars to avoid huge content
            return full_text[:5000]
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except Exception as e:
            print(f"Transcript error for {video_id}: {e}")
            return None
