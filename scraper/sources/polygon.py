"""Polygon.io Data Source - Market news and ticker data."""
import asyncio
from datetime import datetime, timedelta
from typing import AsyncIterator
import httpx

from config import POLYGON_API_KEY, TRACKED_TICKERS
from .base import BaseSource, ContentItem


class PolygonSource(BaseSource):
    """Fetch market news from Polygon.io."""
    
    name = "polygon"
    base_url = "https://api.polygon.io"
    
    def __init__(self):
        self.api_key = POLYGON_API_KEY
    
    async def is_configured(self) -> bool:
        """Check if Polygon is configured."""
        return bool(self.api_key)
    
    async def fetch(self, limit: int = 50) -> AsyncIterator[ContentItem]:
        """Fetch recent market news."""
        if not await self.is_configured():
            print("Polygon API not configured, skipping")
            return
        
        seen_ids = set()
        count = 0
        
        async with httpx.AsyncClient() as client:
            # Fetch general market news
            try:
                async for item in self._fetch_news(client, limit=limit):
                    if item.source_id in seen_ids:
                        continue
                    seen_ids.add(item.source_id)
                    yield item
                    count += 1
                    if count >= limit:
                        return
            except Exception as e:
                print(f"Error fetching Polygon news: {e}")
            
            # Fetch news for specific tickers
            for ticker in TRACKED_TICKERS[:10]:  # Limit tickers per run
                if count >= limit:
                    break
                
                try:
                    async for item in self._fetch_ticker_news(client, ticker, limit=3):
                        if item.source_id in seen_ids:
                            continue
                        seen_ids.add(item.source_id)
                        yield item
                        count += 1
                        if count >= limit:
                            break
                except Exception as e:
                    print(f"Error fetching Polygon news for {ticker}: {e}")
                
                await asyncio.sleep(0.2)  # Rate limiting
    
    async def _fetch_news(self, client: httpx.AsyncClient, limit: int) -> AsyncIterator[ContentItem]:
        """Fetch general market news."""
        try:
            response = await client.get(
                f"{self.base_url}/v2/reference/news",
                params={
                    "apiKey": self.api_key,
                    "limit": limit,
                    "order": "desc",
                },
                timeout=10.0,
            )
            
            if response.status_code != 200:
                print(f"Polygon API error: {response.status_code}")
                return
            
            data = response.json()
            articles = data.get("results", [])
            
            for article in articles:
                yield self._parse_article(article)
                
        except Exception as e:
            print(f"Error in Polygon news fetch: {e}")
    
    async def _fetch_ticker_news(self, client: httpx.AsyncClient, ticker: str, limit: int) -> AsyncIterator[ContentItem]:
        """Fetch news for a specific ticker."""
        try:
            response = await client.get(
                f"{self.base_url}/v2/reference/news",
                params={
                    "apiKey": self.api_key,
                    "ticker": ticker,
                    "limit": limit,
                    "order": "desc",
                },
                timeout=10.0,
            )
            
            if response.status_code != 200:
                return
            
            data = response.json()
            articles = data.get("results", [])
            
            for article in articles:
                yield self._parse_article(article, primary_ticker=ticker)
                
        except Exception as e:
            print(f"Error in Polygon ticker news fetch: {e}")
    
    def _parse_article(self, article: dict, primary_ticker: str = None) -> ContentItem:
        """Parse a Polygon news article into ContentItem."""
        # Parse timestamp
        published_str = article.get("published_utc", "")
        try:
            published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
        except:
            published = datetime.utcnow()
        
        # Get tickers mentioned
        tickers = article.get("tickers", [])
        
        return ContentItem(
            source="polygon",
            source_id=article.get("id", ""),
            title=article.get("title", ""),
            content=article.get("description", "")[:3000],
            url=article.get("article_url", ""),
            author=article.get("author", "") or article.get("publisher", {}).get("name", ""),
            engagement=0,
            published_at=published,
            metadata={
                "tickers": tickers,
                "primary_ticker": primary_ticker,
                "publisher": article.get("publisher", {}).get("name", ""),
                "keywords": article.get("keywords", []),
            }
        )
