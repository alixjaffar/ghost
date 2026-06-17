"""
Ghost Data Fetcher

Coordinates fetching from all data sources and stores in database.
"""
import asyncio
from datetime import datetime
from typing import Optional

from database import Database
from analyzer import ContentAnalyzer
from sources import (
    YouTubeSource,
    ApifyYouTubeSource,
    PolymarketSource,
    StockTwitsSource,
    NewsAPISource,
    PolygonSource,
    QuiverSource,
)
from config import MAX_ITEMS_PER_SOURCE, APIFY_API_TOKEN


class DataFetcher:
    """Fetches data from all configured sources."""
    
    def __init__(self, db: Database):
        self.db = db
        self.analyzer = ContentAnalyzer()
        
        # YouTube: prefer Apify (cloud transcripts, no IP blocks) when a token is
        # configured; otherwise fall back to the direct youtube-transcript-api path.
        youtube_source = ApifyYouTubeSource() if APIFY_API_TOKEN else YouTubeSource()
        if APIFY_API_TOKEN:
            print("YouTube source: Apify (cloud)")
        else:
            print("YouTube source: youtube-transcript-api (direct) — set APIFY_API_TOKEN for reliable cloud scraping")

        # Initialize all sources
        self.sources = [
            youtube_source,
            PolymarketSource(),
            StockTwitsSource(),
            NewsAPISource(),
            PolygonSource(),
            QuiverSource(),
        ]
    
    async def get_source_status(self) -> dict:
        """Get configuration status for all sources."""
        status = {}
        for source in self.sources:
            status[source.name] = await source.is_configured()
        return status
    
    async def fetch_all(self, max_per_source: int = None) -> dict:
        """Fetch from all configured sources."""
        if max_per_source is None:
            max_per_source = MAX_ITEMS_PER_SOURCE
        
        results = {
            "started_at": datetime.utcnow().isoformat(),
            "sources": {},
            "total_items": 0,
            "total_mentions": 0,
        }
        
        for source in self.sources:
            source_result = await self._fetch_source(source, max_per_source)
            results["sources"][source.name] = source_result
            results["total_items"] += source_result["items_fetched"]
            results["total_mentions"] += source_result["mentions_extracted"]
        
        results["completed_at"] = datetime.utcnow().isoformat()
        
        return results
    
    async def fetch_source(self, source_name: str, max_items: int = None) -> dict:
        """Fetch from a specific source."""
        if max_items is None:
            max_items = MAX_ITEMS_PER_SOURCE
        
        for source in self.sources:
            if source.name == source_name:
                return await self._fetch_source(source, max_items)
        
        return {"error": f"Unknown source: {source_name}"}
    
    async def _fetch_source(self, source, max_items: int) -> dict:
        """Fetch and process data from a single source."""
        result = {
            "configured": False,
            "items_fetched": 0,
            "mentions_extracted": 0,
            "errors": [],
        }
        
        # Check if source is configured
        if not await source.is_configured():
            result["errors"].append("Source not configured")
            return result
        
        result["configured"] = True
        
        try:
            async for content in source.fetch(limit=max_items):
                try:
                    # Save content
                    saved = await self.db.save_content(content.to_dict())
                    if saved:
                        result["items_fetched"] += 1
                    
                    # Analyze for tickers and sentiment
                    mentions = await self.analyzer.analyze(content)
                    
                    # Save mentions
                    for mention in mentions:
                        mention["content_id"] = content.id
                        await self.db.save_mention(mention)
                        result["mentions_extracted"] += 1
                        
                except Exception as e:
                    result["errors"].append(f"Item processing error: {str(e)[:100]}")
                    
        except Exception as e:
            result["errors"].append(f"Source fetch error: {str(e)[:200]}")
        
        return result


async def run_fetch_job(db: Database) -> dict:
    """Run a complete fetch job."""
    fetcher = DataFetcher(db)
    
    print(f"[{datetime.utcnow().isoformat()}] Starting fetch job...")
    
    # Check source status
    status = await fetcher.get_source_status()
    print(f"Source status: {status}")
    
    # Fetch from all sources
    results = await fetcher.fetch_all()
    
    print(f"[{datetime.utcnow().isoformat()}] Fetch complete:")
    print(f"  Total items: {results['total_items']}")
    print(f"  Total mentions: {results['total_mentions']}")
    
    for source_name, source_result in results["sources"].items():
        status_str = "✓" if source_result["configured"] else "✗"
        print(f"  {status_str} {source_name}: {source_result['items_fetched']} items, {source_result['mentions_extracted']} mentions")
        if source_result["errors"]:
            for error in source_result["errors"][:3]:
                print(f"    ! {error}")
    
    return results
