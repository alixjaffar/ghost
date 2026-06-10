"""Ghost API - FastAPI backend serving signals to the frontend."""
import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import (
    ANTHROPIC_API_KEY, YOUTUBE_API_KEY, NEWSAPI_KEY, POLYGON_API_KEY, QUIVER_API_KEY,
    DATABASE_PATH, FETCH_INTERVAL_MINUTES,
)
from database import Database
from fetcher import DataFetcher, run_fetch_job
from signals import SignalGenerator


# Global instances
db: Optional[Database] = None
signal_generator: Optional[SignalGenerator] = None
data_fetcher: Optional[DataFetcher] = None
scheduler = None
cached_signals: list = []
cache_timestamp: Optional[datetime] = None
CACHE_TTL_SECONDS = 600  # 10 minutes - AI generation is slow
cache_refreshing: bool = False


async def _initial_cache_warmup():
    """Generate the signal cache in the background so startup is not blocked.

    If the database is empty (e.g. a fresh / ephemeral free-tier host), kick off
    a data fetch first so the app self-populates without manual intervention.
    """
    global cached_signals, cache_timestamp
    if not signal_generator or not db:
        return
    try:
        bootstrap_enabled = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
        content_count = await db.get_content_count()
        if content_count == 0 and bootstrap_enabled:
            print("Empty database detected - bootstrapping with an initial fetch...")
            try:
                await run_fetch_job(db)
            except Exception as e:
                print(f"Bootstrap fetch failed (will retry on schedule): {e}")

        print("Warming up signals cache in background...")
        signals = await signal_generator.generate_all_signals()
        cached_signals = signals
        cache_timestamp = datetime.utcnow()
        print(f"Signals cache ready: {len(signals)} signals")
    except Exception as e:
        print(f"Warning: Could not warm up signals cache: {e}")


async def _scheduled_fetch_job():
    """Periodic data fetch that also refreshes the signal cache afterwards."""
    if not db:
        return
    try:
        await run_fetch_job(db)
    except Exception as e:
        print(f"Scheduled fetch job failed: {e}")
    # Rebuild signals from freshly fetched data
    await refresh_signals_cache()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup."""
    global db, signal_generator, data_fetcher, scheduler

    print("Initializing Ghost API...")

    db = Database(DATABASE_PATH)
    await db.init()

    signal_generator = SignalGenerator(db)
    data_fetcher = DataFetcher(db)

    # Log source status
    status = await data_fetcher.get_source_status()
    print(f"Data sources: {status}")

    # Warm up the cache without blocking startup (API comes up immediately)
    asyncio.create_task(_initial_cache_warmup())

    # Schedule periodic data fetching so signals stay fresh automatically
    if os.getenv("ENABLE_SCHEDULER", "true").lower() == "true":
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            scheduler = AsyncIOScheduler()
            scheduler.add_job(
                _scheduled_fetch_job,
                "interval",
                minutes=FETCH_INTERVAL_MINUTES,
                id="ghost_fetch",
                max_instances=1,
                coalesce=True,
            )
            scheduler.start()
            print(f"Scheduler started: fetching every {FETCH_INTERVAL_MINUTES} min")
        except Exception as e:
            print(f"Warning: Could not start scheduler: {e}")

    yield

    # Shutdown
    if scheduler:
        scheduler.shutdown(wait=False)


app = FastAPI(
    title="Ghost API",
    description="Predictive intelligence for financial markets",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: configurable via ALLOWED_ORIGINS (comma-separated). Falls back to local dev.
_allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if _allowed_origins_env.strip():
    allowed_origins = [o.strip() for o in _allowed_origins_env.split(",") if o.strip()]
else:
    allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================
# Health & Status
# ===========================================

@app.get("/health")
async def health_check():
    """Check API health and source configuration."""
    source_status = await data_fetcher.get_source_status() if data_fetcher else {}
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "sources": source_status,
        "database": "connected" if db else "disconnected",
    }


@app.get("/api/stats")
async def get_stats():
    """Get database and cache statistics."""
    if not db:
        return {"error": "Database not initialized"}
    
    content_count = await db.get_content_count()
    mention_count = await db.get_mention_count()
    
    return {
        "content_items": content_count,
        "ticker_mentions": mention_count,
        "signals_cached": len(cached_signals),
        "cache_age_seconds": (datetime.utcnow() - cache_timestamp).total_seconds() if cache_timestamp else None,
    }


# ===========================================
# Signals
# ===========================================

async def refresh_signals_cache():
    """Background task to refresh the signals cache."""
    global cached_signals, cache_timestamp, cache_refreshing
    
    if cache_refreshing or not signal_generator:
        return
    
    cache_refreshing = True
    try:
        print("Refreshing signals cache...")
        signals = await signal_generator.generate_all_signals()
        cached_signals = signals
        cache_timestamp = datetime.utcnow()
        print(f"Signals cache refreshed: {len(signals)} signals")
    except Exception as e:
        print(f"Failed to refresh signals cache: {e}")
    finally:
        cache_refreshing = False


@app.get("/api/signals")
async def get_signals(
    background_tasks: BackgroundTasks,
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
):
    """Get all signals."""
    global cached_signals, cache_timestamp
    
    now = datetime.utcnow()
    cache_expired = not cache_timestamp or (now - cache_timestamp).total_seconds() >= CACHE_TTL_SECONDS
    
    # If we have cached data, return it immediately
    if cached_signals:
        signals = cached_signals
        # Trigger background refresh if cache is expired
        if cache_expired and not cache_refreshing:
            background_tasks.add_task(refresh_signals_cache)
    else:
        # No cache - must wait for initial generation
        if signal_generator:
            print("No cached signals, generating fresh...")
            signals = await signal_generator.generate_all_signals()
            cached_signals = signals
            cache_timestamp = now
        else:
            signals = []
    
    if status:
        signals = [s for s in signals if s['status'] == status]
    
    return signals[:limit]


@app.get("/api/signals/{signal_id}")
async def get_signal(signal_id: str, background_tasks: BackgroundTasks):
    """Get a specific signal."""
    global cached_signals, cache_timestamp
    
    # Return from cache immediately, refresh in background if needed
    now = datetime.utcnow()
    cache_expired = not cache_timestamp or (now - cache_timestamp).total_seconds() >= CACHE_TTL_SECONDS
    
    if cache_expired and not cache_refreshing and cached_signals:
        background_tasks.add_task(refresh_signals_cache)
    
    for signal in cached_signals:
        if signal['id'] == signal_id:
            return signal
    
    raise HTTPException(status_code=404, detail="Signal not found")


@app.get("/api/search")
async def search_signals(q: str = Query(..., min_length=1), background_tasks: BackgroundTasks = None):
    """Search signals."""
    global cached_signals, cache_timestamp
    
    # Return from cache immediately, refresh in background if needed
    now = datetime.utcnow()
    cache_expired = not cache_timestamp or (now - cache_timestamp).total_seconds() >= CACHE_TTL_SECONDS
    
    if cache_expired and not cache_refreshing and cached_signals and background_tasks:
        background_tasks.add_task(refresh_signals_cache)
    
    query = q.lower()
    return [
        s for s in cached_signals
        if query in s['title'].lower() 
        or query in s['summary'].lower()
        or any(query in t['symbol'].lower() for t in s['relatedTickers'])
    ]


# ===========================================
# Data Fetching
# ===========================================

@app.post("/api/fetch")
async def trigger_fetch(background_tasks: BackgroundTasks):
    """Trigger a data fetch from all sources, then refresh signals."""
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async def fetch_and_refresh():
        await run_fetch_job(db)
        await refresh_signals_cache()

    background_tasks.add_task(fetch_and_refresh)

    return {
        "status": "started",
        "message": "Fetch job started in background",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/fetch/{source}")
async def trigger_source_fetch(source: str, background_tasks: BackgroundTasks):
    """Trigger a fetch from a specific source, then refresh signals."""
    if not data_fetcher:
        raise HTTPException(status_code=500, detail="Fetcher not initialized")

    valid_sources = ["youtube", "stocktwits", "news", "polygon", "reddit"]
    if source not in valid_sources:
        raise HTTPException(status_code=400, detail=f"Invalid source. Must be one of: {valid_sources}")

    async def fetch_single():
        result = await data_fetcher.fetch_source(source)
        print(f"Fetch result for {source}: {result}")
        await refresh_signals_cache()

    background_tasks.add_task(fetch_single)

    return {
        "status": "started",
        "source": source,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ===========================================
# Raw Data
# ===========================================

@app.get("/api/content")
async def get_content(limit: int = Query(50, ge=1, le=200)):
    """Get recent raw content."""
    if not db:
        return []
    return await db.get_recent_content(limit=limit)


@app.get("/api/mentions")
async def get_mentions(limit: int = Query(100, ge=1, le=500)):
    """Get recent ticker mentions."""
    if not db:
        return []
    return await db.get_recent_mentions(limit=limit)


# Legacy endpoint
@app.post("/api/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks):
    """Legacy endpoint - redirects to /api/fetch."""
    return await trigger_fetch(background_tasks)


# ===========================================
# Local Scraper Ingestion
# ===========================================

class IngestRequest(BaseModel):
    items: list[dict]

@app.post("/api/ingest")
async def ingest_content(request: IngestRequest):
    """Ingest content from local scraper."""
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")

    from analyzer import ContentAnalyzer
    from sources.base import ContentItem

    analyzer = ContentAnalyzer()
    ingested = 0
    mentions_saved = 0

    for item in request.items:
        try:
            # Parse published timestamp safely
            published_at = datetime.utcnow()
            if item.get("published_at"):
                try:
                    published_at = datetime.fromisoformat(
                        item["published_at"].replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    pass

            content_item = ContentItem(
                source=item.get("source", "youtube"),
                source_id=item.get("source_id", ""),
                title=item.get("title", ""),
                content=item.get("content", ""),
                url=item.get("url", ""),
                author=item.get("author", ""),
                engagement=item.get("engagement", 0),
                published_at=published_at,
                metadata=item.get("metadata", {}),
            )

            # Save content as a dict (matches Database.save_content signature)
            await db.save_content(content_item.to_dict())

            # Analyze and save mentions (matches fetcher.py pattern)
            mentions = await analyzer.analyze(content_item)
            for mention in mentions:
                mention["content_id"] = content_item.id
                await db.save_mention(mention)
                mentions_saved += 1

            ingested += 1
        except Exception as e:
            print(f"Failed to ingest item: {e}")

    # Invalidate cache so new data appears on next request
    global cache_timestamp
    cache_timestamp = None

    return {
        "status": "success",
        "ingested": ingested,
        "mentions": mentions_saved,
        "total": len(request.items),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
