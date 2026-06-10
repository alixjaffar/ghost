"""Quiver Quantitative Data Source - Reddit sentiment (legally aggregated)."""
import asyncio
from datetime import datetime, timedelta
from typing import AsyncIterator
import httpx

from config import QUIVER_API_KEY, TRACKED_TICKERS
from .base import BaseSource, ContentItem


class QuiverSource(BaseSource):
    """Fetch Reddit sentiment data from Quiver Quantitative (legally aggregated)."""
    
    name = "reddit"  # Label as reddit since it's Reddit-derived data
    base_url = "https://api.quiverquant.com/beta"
    
    def __init__(self):
        self.api_key = QUIVER_API_KEY
    
    async def is_configured(self) -> bool:
        """Check if Quiver is configured."""
        return bool(self.api_key)
    
    async def fetch(self, limit: int = 50) -> AsyncIterator[ContentItem]:
        """Fetch Reddit sentiment data from Quiver."""
        if not await self.is_configured():
            print("Quiver API not configured, skipping")
            return
        
        count = 0
        
        async with httpx.AsyncClient() as client:
            # Fetch WSB mentions
            try:
                async for item in self._fetch_wsb_mentions(client, limit=limit):
                    yield item
                    count += 1
                    if count >= limit:
                        return
            except Exception as e:
                print(f"Error fetching Quiver WSB data: {e}")
            
            # Fetch sentiment for specific tickers
            for ticker in TRACKED_TICKERS[:15]:
                if count >= limit:
                    break
                
                try:
                    async for item in self._fetch_ticker_sentiment(client, ticker):
                        yield item
                        count += 1
                        if count >= limit:
                            break
                except Exception as e:
                    print(f"Error fetching Quiver data for {ticker}: {e}")
                
                await asyncio.sleep(0.3)
    
    async def _fetch_wsb_mentions(self, client: httpx.AsyncClient, limit: int) -> AsyncIterator[ContentItem]:
        """Fetch WallStreetBets mention data."""
        try:
            response = await client.get(
                f"{self.base_url}/historical/wallstreetbets",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=15.0,
            )
            
            if response.status_code != 200:
                print(f"Quiver API error: {response.status_code}")
                return
            
            data = response.json()
            
            # Get recent entries
            recent = sorted(data, key=lambda x: x.get("Date", ""), reverse=True)[:limit]
            
            for entry in recent:
                # Parse date
                date_str = entry.get("Date", "")
                try:
                    published = datetime.strptime(date_str, "%Y-%m-%d")
                except:
                    published = datetime.utcnow()
                
                ticker = entry.get("Ticker", "")
                mentions = entry.get("Mentions", 0)
                rank = entry.get("Rank", 0)
                sentiment = entry.get("Sentiment", 0)
                
                # Create content summary
                content = f"${ticker} had {mentions} mentions on r/wallstreetbets. "
                content += f"Ranked #{rank} for the day. "
                content += f"Sentiment score: {sentiment:.2f}"
                
                yield ContentItem(
                    source="reddit",
                    source_id=f"wsb-{ticker}-{date_str}",
                    title=f"${ticker} - WSB Activity ({mentions} mentions)",
                    content=content,
                    url=f"https://www.reddit.com/r/wallstreetbets/search/?q={ticker}",
                    author="r/wallstreetbets",
                    engagement=mentions,
                    published_at=published,
                    metadata={
                        "ticker": ticker,
                        "mentions": mentions,
                        "rank": rank,
                        "sentiment_score": sentiment,
                        "source": "quiver_wsb",
                    }
                )
                
        except Exception as e:
            print(f"Error in Quiver WSB fetch: {e}")
    
    async def _fetch_ticker_sentiment(self, client: httpx.AsyncClient, ticker: str) -> AsyncIterator[ContentItem]:
        """Fetch sentiment data for a specific ticker."""
        try:
            response = await client.get(
                f"{self.base_url}/historical/wallstreetbets/{ticker}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0,
            )
            
            if response.status_code != 200:
                return
            
            data = response.json()
            
            # Get most recent entry
            if not data:
                return
            
            recent = sorted(data, key=lambda x: x.get("Date", ""), reverse=True)[:1]
            
            for entry in recent:
                date_str = entry.get("Date", "")
                try:
                    published = datetime.strptime(date_str, "%Y-%m-%d")
                except:
                    published = datetime.utcnow()
                
                mentions = entry.get("Mentions", 0)
                sentiment = entry.get("Sentiment", 0)
                
                yield ContentItem(
                    source="reddit",
                    source_id=f"quiver-{ticker}-{date_str}",
                    title=f"${ticker} Reddit Sentiment",
                    content=f"${ticker} sentiment score: {sentiment:.2f} with {mentions} mentions on Reddit investing communities.",
                    url=f"https://www.quiverquant.com/wallstreetbets/{ticker}",
                    author="Quiver Quantitative",
                    engagement=mentions,
                    published_at=published,
                    metadata={
                        "ticker": ticker,
                        "mentions": mentions,
                        "sentiment_score": sentiment,
                        "source": "quiver_ticker",
                    }
                )
                
        except Exception as e:
            print(f"Error in Quiver ticker fetch for {ticker}: {e}")
