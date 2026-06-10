"""StockTwits Data Source - Social sentiment for stocks."""
import asyncio
from datetime import datetime
from typing import AsyncIterator
import httpx

from config import STOCKTWITS_SYMBOLS
from .base import BaseSource, ContentItem


class StockTwitsSource(BaseSource):
    """Fetch messages from StockTwits (no API key required for public endpoints)."""
    
    name = "stocktwits"
    base_url = "https://api.stocktwits.com/api/2"
    
    async def is_configured(self) -> bool:
        """StockTwits public API doesn't require authentication."""
        return True
    
    async def fetch(self, limit: int = 50) -> AsyncIterator[ContentItem]:
        """Fetch recent messages for tracked symbols."""
        messages_per_symbol = max(5, limit // len(STOCKTWITS_SYMBOLS))
        count = 0
        
        async with httpx.AsyncClient() as client:
            for symbol in STOCKTWITS_SYMBOLS:
                if count >= limit:
                    break
                    
                try:
                    async for item in self._fetch_symbol(client, symbol, messages_per_symbol):
                        yield item
                        count += 1
                        if count >= limit:
                            break
                except Exception as e:
                    print(f"Error fetching StockTwits for {symbol}: {e}")
                
                # Rate limiting - StockTwits allows 200 requests per hour
                await asyncio.sleep(0.5)
    
    async def _fetch_symbol(self, client: httpx.AsyncClient, symbol: str, limit: int) -> AsyncIterator[ContentItem]:
        """Fetch messages for a specific symbol."""
        try:
            response = await client.get(
                f"{self.base_url}/streams/symbol/{symbol}.json",
                params={"limit": limit},
                timeout=10.0,
            )
            
            if response.status_code != 200:
                return
            
            data = response.json()
            messages = data.get("messages", [])
            
            for msg in messages:
                # Parse timestamp
                created_at = msg.get("created_at", "")
                try:
                    published = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                except:
                    published = datetime.utcnow()
                
                # Get sentiment if available
                sentiment = msg.get("entities", {}).get("sentiment", {})
                sentiment_str = sentiment.get("basic", "neutral") if sentiment else "neutral"
                
                # Get user info
                user = msg.get("user", {})
                followers = user.get("followers", 0)
                
                yield ContentItem(
                    source="stocktwits",
                    source_id=str(msg.get("id", "")),
                    title=f"${symbol} - {user.get('username', 'Unknown')}",
                    content=msg.get("body", ""),
                    url=f"https://stocktwits.com/{user.get('username', '')}/message/{msg.get('id', '')}",
                    author=user.get("username", ""),
                    author_followers=followers,
                    engagement=msg.get("likes", {}).get("total", 0),
                    published_at=published,
                    metadata={
                        "symbol": symbol,
                        "sentiment": sentiment_str,
                        "reshares": msg.get("reshares", {}).get("total", 0),
                    }
                )
        except httpx.TimeoutException:
            print(f"Timeout fetching StockTwits for {symbol}")
        except Exception as e:
            print(f"Error in StockTwits fetch for {symbol}: {e}")
