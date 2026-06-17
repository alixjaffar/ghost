# Ghost — Deployment Guide

This guide takes Ghost from local code to a live, shippable beta:

- **Frontend** (Next.js) → **Vercel**
- **Backend** (FastAPI) → **Koyeb** (free instance, runs the Dockerfile)
- **Auth** → **Clerk** (free beta, users sign up to access the app)
- **Local scraper** → keeps running on your Mac, posting to the live backend

Total time: ~30–45 minutes. **Cost: $0** to run — Vercel Hobby, Koyeb Free, Clerk free, and the data-source free tiers. (Koyeb requires a credit card to verify your account — a $29 pre-authorization hold that is immediately canceled; you are never charged on the free instance.)

> **Free-tier trade-offs (Koyeb backend):** the free instance scales to zero after ~1h of inactivity, so the first request after idle has a ~1–5s cold start. The database is ephemeral (resets on restart — free instances can't use persistent volumes), but Ghost auto-repopulates it on startup because the DB is just a cache of public scraped data — your users' watchlists live in their browser, so nothing important is lost. When you want always-on + persistent data, move to a paid Koyeb instance with a Volume (see "Paid upgrade" at the end).

---

## 0. Prerequisites — accounts & keys

Create free accounts:

- [GitHub](https://github.com) (to host the code)
- [Vercel](https://vercel.com)
- [Koyeb](https://www.koyeb.com) (will ask for a card to verify — not charged on free)
- [Clerk](https://dashboard.clerk.com)

Have these API keys ready (you already have most):

| Key | Where to get it | Required? |
|-----|-----------------|-----------|
| `ANTHROPIC_API_KEY` | console.anthropic.com | Yes |
| `YOUTUBE_API_KEY` | console.cloud.google.com | Yes |
| `APIFY_API_TOKEN` | console.apify.com → Integrations | Recommended (cloud YouTube transcripts, no IP blocks) |
| `NEWSAPI_KEY` | newsapi.org | Yes |
| `POLYGON_API_KEY` | polygon.io | Recommended |
| `QUIVER_API_KEY` | quiverquant.com | Optional |
| Polymarket | public API — no key | On by default (`POLYMARKET_ENABLED=true`) |
| Clerk Publishable + Secret key | Clerk dashboard → API Keys | Yes |

---

## 1. Push the code to GitHub

A `.gitignore` is already in place so your `.env` files and database are **not** committed.

```bash
cd /Users/alijaffar/GH_ST
git init
git add .
git commit -m "Ghost MVP"
git branch -M main
# Create an empty repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/ghost.git
git push -u origin main
```

> Double-check: `git status` should NOT list `scraper/.env`. If it does, stop and fix `.gitignore` before pushing — that file has your secret keys.

---

## 2. Set up Clerk (auth)

1. In the [Clerk dashboard](https://dashboard.clerk.com), create an application (enable Email + Google).
2. Go to **API Keys** and copy:
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (starts with `pk_...`)
   - `CLERK_SECRET_KEY` (starts with `sk_...`)
3. You'll paste these into Vercel in step 4.

---

## 3. Deploy the backend to Koyeb (free)

Koyeb builds straight from your repo's `Dockerfile` (already in `scraper/`).

1. In the [Koyeb control panel](https://app.koyeb.com): **Create Web Service → GitHub**, and select your repo.
2. **Builder:** choose **Dockerfile**.
3. **Work directory / Build context:** set to `scraper` (this is where the Dockerfile lives). Dockerfile path: `Dockerfile`.
4. **Instance:** select the **Free** instance. **Region:** Washington, D.C. (or Frankfurt).
5. **Exposed port:** `8000`, protocol `HTTP`, route `/` (the Dockerfile already listens on `$PORT`, which Koyeb sets to 8000).
6. **Health check:** HTTP path `/health`.
7. **Environment variables** — add:
   - Secrets: `ANTHROPIC_API_KEY`, `YOUTUBE_API_KEY`, `APIFY_API_TOKEN`, `NEWSAPI_KEY`, `POLYGON_API_KEY`, `QUIVER_API_KEY`
   - `ENABLE_SCHEDULER` = `true`
   - `FETCH_INTERVAL_MINUTES` = `30`
   - `POLYMARKET_ENABLED` = `true`
   - `ALLOWED_ORIGINS` = leave blank for now (set it after you have the Vercel URL in step 5)
8. Deploy. Once live, note your backend URL, e.g. `https://ghost-api-YOURORG.koyeb.app`.
9. Verify: open `https://ghost-api-YOURORG.koyeb.app/health` — you should see `{"status":"healthy",...}`.

**CLI alternative** (if you prefer; install the Koyeb CLI and run `koyeb login` first):

```bash
koyeb app init ghost-api \
  --git github.com/YOUR_USERNAME/ghost \
  --git-branch main \
  --git-builder docker \
  --git-workdir scraper \
  --instance-type free \
  --regions was \
  --ports 8000:http \
  --routes /:8000 \
  --env ENABLE_SCHEDULER=true \
  --env FETCH_INTERVAL_MINUTES=30 \
  --env ANTHROPIC_API_KEY=@ANTHROPIC_API_KEY \
  --env YOUTUBE_API_KEY=@YOUTUBE_API_KEY \
  --env NEWSAPI_KEY=@NEWSAPI_KEY \
  --env POLYGON_API_KEY=@POLYGON_API_KEY \
  --env QUIVER_API_KEY=@QUIVER_API_KEY
```

> On startup the backend checks if its database is empty and, if so, runs an initial data fetch automatically — so a fresh free-tier instance populates itself within a few minutes.
>
> Note: `render.yaml` is also included in the repo if you ever want to deploy to Render instead — Koyeb ignores it.

---

## 4. Deploy the frontend to Vercel

1. In Vercel: **Add New → Project**, import your GitHub repo.
2. **Important:** set **Root Directory** to `frontend`.
3. Add Environment Variables:

   | Name | Value |
   |------|-------|
   | `NEXT_PUBLIC_API_URL` | your Koyeb URL, e.g. `https://ghost-api-YOURORG.koyeb.app` |
   | `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_...` from Clerk |
   | `CLERK_SECRET_KEY` | `sk_...` from Clerk |
   | `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | `/sign-in` |
   | `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | `/sign-up` |
   | `NEXT_PUBLIC_CLERK_SIGN_IN_FALLBACK_REDIRECT_URL` | `/signals` |
   | `NEXT_PUBLIC_CLERK_SIGN_UP_FALLBACK_REDIRECT_URL` | `/signals` |

4. Deploy. Note your frontend URL, e.g. `https://ghost.vercel.app`.

---

## 5. Connect the two (CORS)

1. Back in Koyeb → `ghost-api` → Settings → Environment variables, set:
   - `ALLOWED_ORIGINS` = `https://ghost.vercel.app` (your Vercel URL; add a custom domain later comma-separated)
2. Save — Koyeb redeploys automatically.

Now the frontend can talk to the backend.

---

## 6. Point your local scraper at production (optional)

Your Mac scraper can feed the live backend. In `scraper/.env` (local), add:

```
GHOST_API_URL=https://ghost-api-YOURORG.koyeb.app
```

Then run:

```bash
cd local-scraper
python youtube_scraper.py --daemon
```

It will POST transcripts to the live `/api/ingest`, and signals will refresh automatically.

---

## 7. Smoke test the live app

1. Visit your Vercel URL → you should see the landing page.
2. Click **Get Started** → Clerk sign-up → create an account.
3. You should land on `/signals` with live signals.
4. Open a signal, add to watchlist, search — all should work.

---

## Going from beta → paid (later)

When you're ready to charge, add Stripe via Clerk Billing (Clerk has native subscription support) or Stripe Checkout. The auth layer is already in place, so gating paid features is a small addition.

## Paid upgrade (when you outgrow free)

To get an always-on backend with a persistent database on Koyeb:

1. Switch the service from the **Free** instance to a paid one (e.g. **Eco**, from ~$1.61/mo in select regions, or **Starter**).
2. Attach a **Volume** and mount it at `/data`.
3. Set env var `DATABASE_PATH=/data/ghost.db` so SQLite lives on the volume.

This removes the scale-to-zero sleep and keeps your data across restarts.

## Scaling notes

- **SQLite is fine for the single-instance beta.** If you outgrow one backend instance (heavy concurrent writes or multiple instances), migrate to Postgres. Because `DATABASE_PATH` is the only storage config, the migration is isolated to `database.py`. (Koyeb also offers a free PostgreSQL DB, though it's limited to ~5 hours of active time on the free plan.)
- To reduce cold starts, you can ping `/health` periodically with a free uptime monitor (e.g. UptimeRobot) — note this keeps it warm but the DB is still ephemeral on the free instance.
- Add Sentry (frontend + backend) for error monitoring before a big launch.
