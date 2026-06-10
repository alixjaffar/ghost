"""NewsAPI Data Source - Financial news articles."""
import asyncio
from datetime import datetime, timedelta
from typing import AsyncIterator
import httpx

from config import NEWSAPI_KEY, NEWS_QUERIES
from .base import BaseSource, ContentItem


class NewsAPISource(BaseSource):
    """Fetch financial news from NewsAPI.org."""
    
    name = "news"
    base_url = "https://newsapi.org/v2"
    
    def __init__(self):
        self.api_key = NEWSAPI_KEY
    
    async def is_configured(self) -> bool:
        """Check if NewsAPI is configured."""
        return bool(self.api_key)
    
    async def fetch(self, limit: int = 50) -> AsyncIterator[ContentItem]:
        """Fetch recent news articles."""
        if not await self.is_configured():
            print("NewsAPI not configured, skipping")
            return
        
        articles_per_query = max(5, limit // len(NEWS_QUERIES))
        count = 0
        seen_urls = set()
        
        async with httpx.AsyncClient() as client:
            for query in NEWS_QUERIES:
                if count >= limit:
                    break
                
                try:
                    async for item in self._search_news(client, query, articles_per_query):
                        # Dedupe by URL
                        if item.url in seen_urls:
                            continue
                        seen_urls.add(item.url)
                        
                        yield item
                        count += 1
                        if count >= limit:
                            break
                except Exception as e:
                    print(f"Error fetching news for '{query}': {e}")
                
                # Rate limiting
                await asyncio.sleep(0.5)
    
    async def _search_news(self, client: httpx.AsyncClient, query: str, limit: int) -> AsyncIterator[ContentItem]:
        """Search for news articles matching a query."""
        # Get news from last 7 days
        from_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        try:
            response = await client.get(
                f"{self.base_url}/everything",
                params={
                    "apiKey": self.api_key,
                    "q": query,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": limit,
                    "from": from_date,
                },
                timeout=10.0,
            )
            
            if response.status_code != 200:
                error = response.json().get("message", "Unknown error")
                print(f"NewsAPI error: {error}")
                return
            
            data = response.json()
            articles = data.get("articles", [])
            
            for article in articles:
                # Parse timestamp
                published_str = article.get("publishedAt", "")
                try:
                    published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                except:
                    published = datetime.utcnow()
                
                # Combine title, description, and content
                content_parts = [
                    article.get("title", ""),
                    article.get("description", ""),
                    article.get("content", ""),
                ]
                full_content = " ".join(filter(None, content_parts))
                
                yield ContentItem(
                    source="news",
                    source_id=article.get("url", ""),
                    title=article.get("title", ""),
                    content=full_content[:3000],  # Limit content size
                    url=article.get("url", ""),
                    author=article.get("author", "") or article.get("source", {}).get("name", ""),
                    engagement=0,  # NewsAPI doesn't provide engagement metrics
                    published_at=published,
                    metadata={
                        "source_name": article.get("source", {}).get("name", ""),
                        "query": query,
                    }
                )
        except httpx.TimeoutException:
            print(f"Timeout fetching news for '{query}'")
        except Exception as e:
            print(f"Error in news search for '{query}': {e}")
