#!/usr/bin/env python3
"""
Ghost Local YouTube Scraper
============================
Runs on your Mac to fetch YouTube transcripts without IP blocking.

Usage:
    python youtube_scraper.py              # Run once
    python youtube_scraper.py --daemon     # Run continuously every 30 minutes

Requirements:
    pip install youtube-transcript-api google-api-python-client requests python-dotenv
"""

import os
import sys
import time
import json
import argparse
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment from parent scraper directory
env_path = Path(__file__).parent.parent / "scraper" / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GHOST_API_URL = os.getenv("GHOST_API_URL", "http://localhost:8000")
FETCH_INTERVAL_MINUTES = int(os.getenv("LOCAL_FETCH_INTERVAL", "30"))

# Proxy configuration (optional - for avoiding IP blocks)
# Format: http://user:pass@host:port or http://host:port
PROXY_URL = os.getenv("PROXY_URL", None)

# Finance YouTube channels to monitor
YOUTUBE_CHANNELS = [
    "UC4sOcJvlWBV77YVJ6nJB4Xw",  # Meet Kevin
    "UCIp-X0RmcUfhqXC8_VVeQJw",  # Financial Education
    "UCGy7SkBjcIAgTiwkXEtPnYg",  # Andrei Jikh
    "UCfpnY5NnBl-8L7SvICuYkYQ",  # Graham Stephan
    "UCnMn36GT_H0X-w5_ckLtlgQ",  # Patrick Boyle
    "UCVwznenKF-V8qYsQ_6WsLdA",  # Tom Nash
    "UCbta0n8i6Rljh0obO7HzG9A",  # Ben Felix
]

# Search terms for discovering finance videos
SEARCH_TERMS = [
    "NVDA stock analysis",
    "AI chip shortage 2026",
    "semiconductor stocks",
    "GLP-1 Ozempic investing",
    "nuclear energy stocks",
    "uranium stocks",
    "data center power demand",
]


def log(message: str):
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_channel_videos(channel_id: str, max_results: int = 5) -> list[str]:
    """Get recent video IDs from a YouTube channel."""
    if not YOUTUBE_API_KEY:
        return []
    
    try:
        # Get uploads playlist
        url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "key": YOUTUBE_API_KEY,
            "id": channel_id,
            "part": "contentDetails",
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if not data.get("items"):
            return []
        
        uploads_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Get videos from uploads
        url = "https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            "key": YOUTUBE_API_KEY,
            "playlistId": uploads_id,
            "part": "contentDetails",
            "maxResults": max_results,
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        return [item["contentDetails"]["videoId"] for item in data.get("items", [])]
    except Exception as e:
        log(f"Error fetching channel {channel_id}: {e}")
        return []


def search_videos(query: str, max_results: int = 5) -> list[str]:
    """Search YouTube for videos matching a query."""
    if not YOUTUBE_API_KEY:
        return []
    
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": YOUTUBE_API_KEY,
            "q": query,
            "type": "video",
            "part": "id",
            "maxResults": max_results,
            "order": "date",
            "publishedAfter": "2024-01-01T00:00:00Z",
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        return [item["id"]["videoId"] for item in data.get("items", [])]
    except Exception as e:
        log(f"Error searching '{query}': {e}")
        return []


def get_video_metadata(video_id: str) -> dict | None:
    """Get video metadata from YouTube API."""
    if not YOUTUBE_API_KEY:
        return None
    
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "key": YOUTUBE_API_KEY,
            "id": video_id,
            "part": "snippet,statistics",
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if not data.get("items"):
            return None
        
        video = data["items"][0]
        snippet = video["snippet"]
        stats = video.get("statistics", {})
        
        return {
            "video_id": video_id,
            "title": snippet.get("title", ""),
            "description": snippet.get("description", "")[:2000],
            "channel_title": snippet.get("channelTitle", ""),
            "channel_id": snippet.get("channelId", ""),
            "published_at": snippet.get("publishedAt", ""),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
        }
    except Exception as e:
        log(f"Error fetching metadata for {video_id}: {e}")
        return None


def get_transcript(video_id: str, retries: int = 2) -> str | None:
    """Get video transcript using youtube-transcript-api with retry logic."""
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
    
    for attempt in range(retries + 1):
        try:
            # Use proxy if configured
            if PROXY_URL:
                from youtube_transcript_api.proxies import WebshareProxyConfig, GenericProxyConfig
                # Generic proxy format: http://user:pass@host:port
                proxy_config = GenericProxyConfig(
                    http_url=PROXY_URL,
                    https_url=PROXY_URL,
                )
                ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
            else:
                ytt_api = YouTubeTranscriptApi()
            
            transcript_list = ytt_api.fetch(video_id)
            
            # Combine transcript segments
            full_text = " ".join([segment.text for segment in transcript_list])
            
            # Limit to ~5000 chars
            return full_text[:5000]
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            log(f"Transcript unavailable for {video_id}: {type(e).__name__}")
            return None
        except Exception as e:
            error_type = type(e).__name__
            if "IpBlocked" in str(e) or "IpBlocked" in error_type:
                if attempt < retries:
                    wait = 10 * (attempt + 1)  # 10s, 20s
                    log(f"IP rate limited, waiting {wait}s before retry...")
                    time.sleep(wait)
                    continue
                else:
                    log(f"Transcript blocked for {video_id} after {retries + 1} attempts")
                    return None
            log(f"Transcript unavailable for {video_id}: {error_type}")
            return None
    return None


def send_to_ghost_api(content_items: list[dict]) -> bool:
    """Send scraped content to Ghost API."""
    if not content_items:
        return True
    
    try:
        # Ghost API expects content to be saved via the fetch endpoint
        # We'll use a direct database endpoint if available, or trigger analysis
        url = f"{GHOST_API_URL}/api/ingest"
        response = requests.post(url, json={"items": content_items}, timeout=30)
        
        if response.status_code == 404:
            # Endpoint doesn't exist yet, just log success
            log(f"Note: /api/ingest not implemented. Content saved locally.")
            # Save locally as backup
            save_local_backup(content_items)
            return True
        
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        log("Ghost API not running. Saving content locally.")
        save_local_backup(content_items)
        return True
    except Exception as e:
        log(f"Error sending to API: {e}")
        return False


def save_local_backup(content_items: list[dict]):
    """Save content to local JSON file as backup."""
    backup_dir = Path(__file__).parent / "data"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"youtube_{timestamp}.json"
    
    with open(backup_file, "w") as f:
        json.dump(content_items, f, indent=2)
    
    log(f"Saved {len(content_items)} items to {backup_file}")


def run_scrape():
    """Run a single scrape cycle."""
    log("Starting YouTube scrape...")
    
    if not YOUTUBE_API_KEY:
        log("ERROR: YOUTUBE_API_KEY not set. Check your .env file.")
        return
    
    video_ids = set()
    
    # Get videos from channels
    log(f"Fetching from {len(YOUTUBE_CHANNELS)} channels...")
    for channel_id in YOUTUBE_CHANNELS:
        ids = get_channel_videos(channel_id, max_results=3)
        video_ids.update(ids)
        time.sleep(0.3)  # Rate limiting
    
    # Get videos from search
    log(f"Searching {len(SEARCH_TERMS)} terms...")
    for query in SEARCH_TERMS:
        ids = search_videos(query, max_results=3)
        video_ids.update(ids)
        time.sleep(0.3)
    
    log(f"Found {len(video_ids)} unique videos")
    
    # Process each video
    content_items = []
    transcripts_fetched = 0
    ip_blocked_count = 0
    
    for i, video_id in enumerate(video_ids):
        log(f"Processing video {i+1}/{len(video_ids)}: {video_id}")
        
        # Get metadata
        metadata = get_video_metadata(video_id)
        if not metadata:
            continue
        
        # Get transcript (this is the valuable part!)
        # Add longer delay if we're getting rate limited
        if ip_blocked_count > 3:
            log("Multiple blocks detected, adding extra delay...")
            time.sleep(5)
        
        transcript = get_transcript(video_id)
        
        # Track blocks
        if transcript is None:
            ip_blocked_count += 1
        else:
            ip_blocked_count = max(0, ip_blocked_count - 1)  # Decay on success
        
        # Use transcript if available, otherwise fall back to description
        content = transcript if transcript else metadata["description"]
        
        if transcript:
            transcripts_fetched += 1
        
        content_items.append({
            "source": "youtube",
            "source_id": video_id,
            "title": metadata["title"],
            "content": content,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "author": metadata["channel_title"],
            "engagement": metadata["view_count"],
            "published_at": metadata["published_at"],
            "has_transcript": transcript is not None,
            "metadata": {
                "likes": metadata["like_count"],
                "comments": metadata["comment_count"],
                "channel_id": metadata["channel_id"],
            }
        })
        
        # Be nice to YouTube - spread requests (2s between each)
        time.sleep(2)
    
    log(f"Processed {len(content_items)} videos ({transcripts_fetched} with transcripts)")
    
    # Send to Ghost API or save locally
    send_to_ghost_api(content_items)
    
    log("Scrape complete!")
    return len(content_items)


def main():
    parser = argparse.ArgumentParser(description="Ghost Local YouTube Scraper")
    parser.add_argument("--daemon", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=FETCH_INTERVAL_MINUTES, 
                        help="Minutes between scrapes (daemon mode)")
    args = parser.parse_args()
    
    log("=" * 50)
    log("Ghost Local YouTube Scraper")
    log("=" * 50)
    log(f"YouTube API Key: {'✓ Configured' if YOUTUBE_API_KEY else '✗ Missing'}")
    log(f"Proxy: {'✓ ' + PROXY_URL.split('@')[-1] if PROXY_URL else '✗ No proxy (may get IP blocked)'}")
    log(f"Ghost API URL: {GHOST_API_URL}")
    log(f"Channels to monitor: {len(YOUTUBE_CHANNELS)}")
    log(f"Search terms: {len(SEARCH_TERMS)}")
    log("=" * 50)
    
    if args.daemon:
        log(f"Running in daemon mode (every {args.interval} minutes)")
        log("Press Ctrl+C to stop")
        
        while True:
            try:
                run_scrape()
                log(f"Sleeping for {args.interval} minutes...")
                time.sleep(args.interval * 60)
            except KeyboardInterrupt:
                log("Stopped by user")
                break
    else:
        run_scrape()


if __name__ == "__main__":
    main()
