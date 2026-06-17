"""Database layer for Ghost - stores scraped content and ticker mentions."""
import aiosqlite
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class Database:
    """SQLite database for Ghost data storage."""
    
    def __init__(self, db_path: str = "data/ghost.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def init(self):
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            # Content items table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS content (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    author TEXT,
                    author_followers INTEGER DEFAULT 0,
                    title TEXT,
                    content TEXT,
                    url TEXT,
                    engagement INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    scraped_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)

            # Migration: add metadata column to pre-existing databases.
            cursor = await db.execute("PRAGMA table_info(content)")
            columns = [row[1] for row in await cursor.fetchall()]
            if "metadata" not in columns:
                await db.execute("ALTER TABLE content ADD COLUMN metadata TEXT")
            
            # Ticker mentions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS mentions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    sentiment TEXT,
                    confidence REAL,
                    context TEXT,
                    price_target REAL,
                    timeframe TEXT,
                    analyzed_at TEXT NOT NULL,
                    FOREIGN KEY (content_id) REFERENCES content(id)
                )
            """)
            
            # Create indexes for performance
            await db.execute("CREATE INDEX IF NOT EXISTS idx_content_platform ON content(platform)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_content_created ON content(created_at)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_mentions_ticker ON mentions(ticker)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_mentions_analyzed ON mentions(analyzed_at)")
            
            await db.commit()
    
    async def save_content(self, content: dict) -> bool:
        """Save a content item."""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT OR REPLACE INTO content
                    (id, platform, author, author_followers, title, content, url, engagement, created_at, scraped_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    content.get('id'),
                    content.get('platform'),
                    content.get('author'),
                    content.get('author_followers', 0),
                    content.get('title'),
                    content.get('content'),
                    content.get('url'),
                    content.get('engagement', 0),
                    content.get('created_at'),
                    datetime.utcnow().isoformat(),
                    json.dumps(content.get('metadata') or {}),
                ))
                await db.commit()
                return True
            except Exception as e:
                print(f"Error saving content: {e}")
                return False
    
    async def save_mention(self, mention: dict) -> bool:
        """Save a ticker mention."""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO mentions 
                    (content_id, ticker, sentiment, confidence, context, price_target, timeframe, analyzed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mention.get('content_id'),
                    mention.get('ticker'),
                    mention.get('sentiment'),
                    mention.get('confidence'),
                    mention.get('context'),
                    mention.get('price_target'),
                    mention.get('timeframe'),
                    datetime.utcnow().isoformat(),
                ))
                await db.commit()
                return True
            except Exception as e:
                print(f"Error saving mention: {e}")
                return False
    
    async def get_recent_mentions(self, since: Optional[datetime] = None, limit: int = 10000) -> list[dict]:
        """Get recent ticker mentions with content metadata."""
        if since is None:
            since = datetime.utcnow() - timedelta(days=7)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT 
                    m.id,
                    m.content_id,
                    m.ticker,
                    m.sentiment,
                    m.confidence,
                    m.context,
                    m.price_target,
                    m.timeframe,
                    m.analyzed_at,
                    c.platform,
                    c.author,
                    c.title,
                    c.engagement,
                    c.created_at,
                    c.url
                FROM mentions m
                JOIN content c ON m.content_id = c.id
                WHERE m.analyzed_at >= ?
                ORDER BY m.analyzed_at DESC
                LIMIT ?
            """, (since.isoformat(), limit))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_recent_content(self, limit: int = 50) -> list[dict]:
        """Get recent scraped content."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM content 
                ORDER BY scraped_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_platform_content(
        self, platform: str, since: Optional[datetime] = None, limit: int = 200
    ) -> list[dict]:
        """Get recent content for one platform, with metadata parsed from JSON."""
        if since is None:
            since = datetime.utcnow() - timedelta(days=7)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM content
                WHERE platform = ? AND created_at >= ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (platform, since.isoformat(), limit))

            rows = await cursor.fetchall()
            results = []
            for row in rows:
                item = dict(row)
                try:
                    item["metadata"] = json.loads(item.get("metadata") or "{}")
                except (json.JSONDecodeError, TypeError):
                    item["metadata"] = {}
                results.append(item)
            return results

    async def get_content_count(self) -> int:
        """Get total content count."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM content")
            row = await cursor.fetchone()
            return row[0] if row else 0
    
    async def get_mention_count(self) -> int:
        """Get total mention count."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM mentions")
            row = await cursor.fetchone()
            return row[0] if row else 0
    
    async def get_ticker_stats(self, ticker: str, days: int = 7) -> dict:
        """Get statistics for a specific ticker."""
        since = datetime.utcnow() - timedelta(days=days)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get mention count and sentiment breakdown
            cursor = await db.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN sentiment = 'bullish' THEN 1 ELSE 0 END) as bullish,
                    SUM(CASE WHEN sentiment = 'bearish' THEN 1 ELSE 0 END) as bearish,
                    SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral
                FROM mentions
                WHERE ticker = ? AND analyzed_at >= ?
            """, (ticker, since.isoformat()))
            
            row = await cursor.fetchone()
            
            return {
                'ticker': ticker,
                'total_mentions': row['total'] if row else 0,
                'bullish': row['bullish'] if row else 0,
                'bearish': row['bearish'] if row else 0,
                'neutral': row['neutral'] if row else 0,
            }
