# Ghost Production Setup Guide

This guide walks you through setting up Ghost with all data sources.

## Data Sources

| Source | What It Provides | Cost | Setup Time |
|--------|------------------|------|------------|
| **Anthropic** | AI analysis (ticker extraction, sentiment) | Pay-as-you-go (~$5-15/day) | 2 min |
| **YouTube** | Video transcripts, financial commentary | Free (10K req/day) | 5 min |
| **NewsAPI** | Financial news articles | Free (500 req/day) | 2 min |
| **StockTwits** | Social sentiment, no key needed | Free | 0 min |
| **Polygon.io** | Market news, ticker data | Free tier | 3 min |
| **Quiver** | Reddit sentiment (legally aggregated) | Free tier | 3 min |

---

## Step 1: Get API Keys

### Anthropic (Required)
You already have this: `sk-ant-api03-...`

### YouTube Data API (Required)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project called "Ghost"
3. Go to **APIs & Services** → **Library**
4. Search for "YouTube Data API v3" and **Enable** it
5. Go to **APIs & Services** → **Credentials**
6. Click **Create Credentials** → **API Key**
7. Copy the key (starts with `AIza...`)

### NewsAPI (Required)
1. Go to [newsapi.org/register](https://newsapi.org/register)
2. Create a free account
3. Copy your API key from the dashboard

### Polygon.io (Recommended)
1. Go to [polygon.io/dashboard/signup](https://polygon.io/dashboard/signup)
2. Create a free account
3. Copy your API key from the dashboard

### Quiver Quantitative (Recommended)
1. Go to [quiverquant.com](https://www.quiverquant.com/)
2. Create a free account
3. Go to API settings and get your key

---

## Step 2: Configure Environment

```bash
cd /Users/alijaffar/GH_ST/scraper

# Copy the example config
cp .env.example .env

# Edit with your keys
nano .env
```

Fill in your `.env` file:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
YOUTUBE_API_KEY=AIza-your-key-here
NEWSAPI_KEY=your-newsapi-key-here

# Recommended
POLYGON_API_KEY=your-polygon-key-here
QUIVER_API_KEY=your-quiver-key-here
```

---

## Step 3: Install Dependencies

```bash
# Backend
cd /Users/alijaffar/GH_ST/scraper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend (if not already done)
cd /Users/alijaffar/GH_ST/frontend
npm install
```

---

## Step 4: Start Ghost

### Option A: Use the startup script
```bash
cd /Users/alijaffar/GH_ST
./start-ghost.sh
```

### Option B: Start manually
```bash
# Terminal 1: Backend
cd /Users/alijaffar/GH_ST/scraper
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd /Users/alijaffar/GH_ST/frontend
npm run dev
```

---

## Step 5: Fetch Data

Once Ghost is running, trigger a data fetch:

```bash
# Fetch from all sources
curl -X POST http://localhost:8000/api/fetch

# Or fetch from individual sources
curl -X POST http://localhost:8000/api/fetch/youtube
curl -X POST http://localhost:8000/api/fetch/stocktwits
curl -X POST http://localhost:8000/api/fetch/news
curl -X POST http://localhost:8000/api/fetch/polygon
curl -X POST http://localhost:8000/api/fetch/reddit
```

Check the results:
```bash
# View stats
curl http://localhost:8000/api/stats

# View raw content
curl http://localhost:8000/api/content?limit=10

# View extracted mentions
curl http://localhost:8000/api/mentions?limit=10

# View generated signals
curl http://localhost:8000/api/signals
```

---

## Step 6: View in Browser

Open http://localhost:3000 to see Ghost with real data!

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check API health and source status |
| `/api/stats` | GET | Database statistics |
| `/api/signals` | GET | Get all signals |
| `/api/signals/{id}` | GET | Get specific signal |
| `/api/search?q=` | GET | Search signals |
| `/api/fetch` | POST | Trigger fetch from all sources |
| `/api/fetch/{source}` | POST | Fetch from specific source |
| `/api/content` | GET | Raw content items |
| `/api/mentions` | GET | Extracted ticker mentions |

---

## Troubleshooting

### "Source not configured"
Check that your API key is correctly set in `.env`

### YouTube quota exceeded
Free tier allows 10,000 units/day. Each search costs ~100 units.
Wait 24 hours or upgrade to paid tier.

### NewsAPI "rateLimited"  
Free tier allows 500 requests/day. Wait or upgrade.

### No signals generated
You need at least 10-20 content items with ticker mentions.
Run multiple fetches or wait for more data.

### AI analysis failing
Check your Anthropic API key and account balance.

---

## Cost Estimates

| Source | Daily Cost |
|--------|------------|
| Anthropic (1000 analyses) | ~$2-5 |
| YouTube | Free |
| NewsAPI | Free |
| StockTwits | Free |
| Polygon | Free |
| Quiver | Free |

**Total: ~$2-5/day for MVP testing**

---

## Next Steps

1. **Set up scheduled fetching**: Use cron or a task scheduler to run fetches every 30 minutes
2. **Add more sources**: Implement additional data sources as needed  
3. **Deploy**: Host on Railway, Render, or AWS
4. **Monitor**: Set up logging and alerting for production
