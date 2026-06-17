# Ghost

**The future is hiding in plain sight.**

Ghost is a predictive intelligence platform for financial markets. It scans conversations across the internet, analyzes them with AI, and surfaces market narratives as they accelerate — before they become headlines.

## Architecture

Ghost is a full-stack app:

```
┌──────────────────────┐     ┌───────────────────────┐     ┌────────────────────┐
│   Data Sources       │────▶│   Backend (FastAPI)   │────▶│  Frontend (Next.js)│
│                      │     │                       │     │                    │
│ - YouTube via Apify  │     │ - Ingest + store      │     │ - Landing          │
│ - Polymarket (odds)  │     │ - Claude analysis     │     │ - Signal feed      │
│ - StockTwits         │     │ - Signal generation   │     │   (Narratives +    │
│ - NewsAPI            │     │ - Prediction signals  │     │    Markets lanes)  │
│ - Polygon.io         │     │ - Auto-fetch scheduler│     │ - Signal detail    │
│ - Quiver (Reddit)    │     │ - REST API + cache    │     │ - Watchlist/Search │
└──────────────────────┘     └───────────────────────┘     └────────────────────┘
        │                                                   ▲
        └──── local-scraper (optional fallback if no Apify) ┘
```

**Two kinds of signals:**
- **Narratives** — clustered ticker mentions from social/news/video, scored heuristically.
- **Prediction markets** — trending finance/crypto/macro markets from **Polymarket**, carrying *real traded odds* as the event probability (not an estimate).

- **Frontend** — `frontend/` — Next.js 16, TypeScript, Tailwind 4, shadcn/ui, Recharts, Clerk auth.
- **Backend** — `scraper/` — FastAPI, SQLite (aiosqlite), Anthropic Claude, APScheduler.
- **Local scraper** — `local-scraper/` — runs on your Mac to pull YouTube transcripts without cloud-IP blocking, POSTing to the backend's `/api/ingest`.

## Quick Start (local)

### 1. Backend

```bash
cd scraper
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then fill in your API keys
uvicorn api:app --reload --port 8000
```

Backend runs at http://localhost:8000 (`/health` to verify, `/docs` for the API).

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # set NEXT_PUBLIC_API_URL + Clerk keys
npm run dev
```

Open http://localhost:3000.

### 3. (Optional) Local YouTube scraper

```bash
cd local-scraper
pip install youtube-transcript-api google-api-python-client requests python-dotenv
python youtube_scraper.py --daemon
```

## Environment Variables

- Backend keys: see `scraper/.env.example` (Anthropic, YouTube, **Apify**, **Polymarket**, NewsAPI, Polygon, Quiver, CORS, DB path, scheduler).
- Frontend keys: see `frontend/.env.example` (`NEXT_PUBLIC_API_URL`, Clerk publishable/secret keys).

### YouTube via Apify (recommended for cloud)

The default YouTube path uses `youtube-transcript-api`, which gets the server's IP
blocked when run in the cloud — the reason the project ships with a local Mac
scraper. Set **`APIFY_API_TOKEN`** and Ghost fetches video transcripts through
Apify's cloud instead, so the hosted backend works without your Mac running. The
actor is overridable via `APIFY_YOUTUBE_ACTOR` (default `streamers~youtube-scraper`),
and you can supply a full actor input with `APIFY_YOUTUBE_INPUT`. Every source
degrades gracefully — Ghost ships and runs even before you add the token.

### Polymarket (no key)

Polymarket uses a public API, so no key is needed — it's on by default
(`POLYMARKET_ENABLED=true`). Ghost pulls the most actively traded finance/crypto/
macro markets and surfaces them as **prediction signals** with real implied odds.

## Features

- **Signal Feed** — narratives ranked by acceleration & event probability, with status (breaking / accelerating / emerging / cooling), confidence, velocity, and related tickers. Filter by **Narratives** or **Markets** lane.
- **Prediction Markets** — live Polymarket finance/crypto/macro markets as signals, with real traded odds, 24h odds moves, volume, and mapped tickers (e.g. Fed → TLT/SPY, Bitcoin → IBIT/COIN/MSTR).
- **Signal Detail** — probability ring, 14-day velocity chart, AI insight, evidence timeline, source breakdown.
- **Watchlist** — track signals & tickers (browser-local).
- **Search** — across narratives, tickers, companies.
- **Auth** — Clerk-gated app (free sign-up); public landing page.

## How signals are generated

1. Sources are fetched on a schedule (`FETCH_INTERVAL_MINUTES`, default 30) or on demand via `POST /api/fetch`.
2. Each item is analyzed by Claude for tickers + sentiment (regex fallback if AI is unavailable).
3. Mentions are clustered into narratives and scored (acceleration, confidence, probability).
4. Signals are cached in-memory (10-min TTL) and refreshed in the background.

## Key API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Health + source config |
| `GET /api/signals` | Ranked signals (cached) |
| `GET /api/signals/{id}` | Single signal |
| `GET /api/search?q=` | Search signals |
| `POST /api/fetch` | Trigger a fetch + refresh |
| `POST /api/ingest` | Ingest from the local scraper |
| `GET /api/stats` | Content/mention counts |

## Deployment

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** — Vercel (frontend) + Render (backend, persistent SQLite) + Clerk, end to end.

## Tech Stack

- **Frontend**: Next.js 16, TypeScript, Tailwind CSS 4, shadcn/ui, Recharts, Lucide, Clerk
- **Backend**: FastAPI, aiosqlite, Anthropic Claude, APScheduler, httpx

## Disclaimer

All scores and probabilities measure social/media momentum and are **not financial advice** or guarantees of market outcomes. Always do your own research.

---

**Ghost** — See it first. Act first. · *Powered by Avallon*
