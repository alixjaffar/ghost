"""Ghost configuration - Production settings."""
import os
from dotenv import load_dotenv

load_dotenv()

# ===========================================
# API Keys
# ===========================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

# ===========================================
# Apify - Cloud YouTube scraping (no IP blocks)
# ===========================================
# When set, Ghost uses Apify to discover YouTube videos and pull transcripts in
# the cloud, replacing the brittle youtube-transcript-api path that gets the
# server's IP blocked. Get a token at https://console.apify.com/account/integrations
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
# Actor that scrapes YouTube videos + subtitles. Use the "user~actor" slug form.
APIFY_YOUTUBE_ACTOR = os.getenv("APIFY_YOUTUBE_ACTOR", "streamers~youtube-scraper")
# Max videos Apify returns per search term / channel (keeps runs cheap + fast).
APIFY_MAX_RESULTS_PER_QUERY = int(os.getenv("APIFY_MAX_RESULTS_PER_QUERY", "4"))
# Optional raw JSON to fully override the actor input (escape hatch for other actors).
APIFY_YOUTUBE_INPUT = os.getenv("APIFY_YOUTUBE_INPUT")

# ===========================================
# Polymarket - Prediction market odds (public Gamma API, no key)
# ===========================================
POLYMARKET_ENABLED = os.getenv("POLYMARKET_ENABLED", "true").lower() == "true"
POLYMARKET_GAMMA_URL = os.getenv("POLYMARKET_GAMMA_URL", "https://gamma-api.polymarket.com")
# How many finance-relevant markets to surface as signals.
POLYMARKET_MAX_MARKETS = int(os.getenv("POLYMARKET_MAX_MARKETS", "12"))
# Only markets whose question/description match these keywords are kept. This is
# what scopes Polymarket to *finance* (stocks, crypto, Fed/macro) instead of
# sports/pop-culture markets.
POLYMARKET_KEYWORDS = [
    # Equities / markets
    "stock", "stocks", "s&p", "sp500", "nasdaq", "dow", "earnings", "ipo",
    "nvidia", "tesla", "apple", "microsoft", "amazon", "meta", "google",
    "market cap", "all-time high", "all time high", "share price",
    # Crypto
    "bitcoin", "btc", "ethereum", "eth", "solana", "sol", "crypto",
    "coinbase", "microstrategy", "etf", "dogecoin", "xrp", "stablecoin",
    # Macro / Fed
    "fed", "federal reserve", "interest rate", "rate cut", "rate hike",
    "recession", "inflation", "cpi", "gdp", "jobs report", "unemployment",
    "treasury", "yield", "tariff", "oil price", "gold price",
]

# ===========================================
# Database
# ===========================================
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/ghost.db")

# ===========================================
# AI Models
# ===========================================
# Configurable via env so models can be swapped without code changes
# (important: model versions get deprecated / reach end-of-life over time).
# Bulk model: fast/cheap for ticker + sentiment extraction.
BULK_MODEL = os.getenv("BULK_MODEL", "claude-sonnet-4-5-20250929")
# Insight model: highest quality for narrative/insight generation.
INSIGHT_MODEL = os.getenv("INSIGHT_MODEL", "claude-opus-4-1-20250805")

# ===========================================
# Fetch Settings
# ===========================================
FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES", "30"))
MAX_ITEMS_PER_SOURCE = int(os.getenv("MAX_ITEMS_PER_SOURCE", "50"))

# ===========================================
# YouTube Channels to Monitor
# ===========================================
# Finance/investing focused channels
# Format: Channel ID (get from youtube.com/@channel -> About -> Share Channel -> Copy ID)
YOUTUBE_CHANNELS = [
    # Financial Education
    "UC4sOcJvlWBV77YVJ6nJB4Xw",  # Meet Kevin
    "UCIp-X0RmcUfhqXC8_VVeQJw",  # Financial Education
    "UCGy7SkBjcIAgTiwkXEtPnYg",  # Andrei Jikh
    "UCfpnY5NnBl-8L7SvICuYkYQ",  # Graham Stephan
    "UCnMn36GT_H0X-w5_ckLtlgQ",  # Patrick Boyle
    "UCVwznenKF-V8qYsQ_6WsLdA",  # Tom Nash
    # Market Analysis
    "UCbta0n8i6Rljh0obO7HzG9A",  # Ben Felix
    "UCJgHN6gk0cV7OWgjfCqdjsQ",  # Everything Money
    # Stocks / Trading desks
    "UC5cEHfCr6WOE1R1zcohd1IA",  # Jose Najarro Stocks (@JoseNajarroStocks)
    "UCRAOycPjsSgcEyQcuJD_ENA",  # RiskReversal Media (@RiskReversalMedia)
    # Financial News networks
    "UCvJJ_dzjViJCoLf5uKUTwoA",  # CNBC (@CNBC)
    "UCUMZ7gohGI9HcU9VNsr2FJQ",  # Bloomberg (@business)
]

# Search terms for YouTube discovery
YOUTUBE_SEARCH_TERMS = [
    "NVDA stock analysis",
    "AI chip shortage",
    "semiconductor stocks",
    "GLP-1 Ozempic investing",
    "nuclear energy stocks",
    "data center power",
    "copper supply",
    "uranium stocks",
]

# ===========================================
# StockTwits - Symbols to Track
# ===========================================
STOCKTWITS_SYMBOLS = [
    # Mega cap tech
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
    # Semiconductors
    "AMD", "INTC", "AVGO", "QCOM", "TSM", "ASML", "MU",
    # AI plays
    "PLTR", "AI", "PATH",
    # Energy
    "VST", "CEG", "NRG",
    # Nuclear/Uranium
    "CCJ", "SMR", "UEC",
    # Pharma/GLP-1
    "LLY", "NVO", "HIMS",
    # Commodities
    "FCX", "SCCO",
    # Shipping
    "ZIM", "SBLK",
]

# ===========================================
# News API - Search Queries
# ===========================================
NEWS_QUERIES = [
    "NVIDIA GPU shortage",
    "AI chip supply",
    "semiconductor shortage",
    "data center power demand",
    "GLP-1 Ozempic Wegovy",
    "nuclear energy AI",
    "uranium stocks",
    "copper supply deficit",
    "shipping rates Red Sea",
    "Tesla robot Optimus",
]

# ===========================================
# Tracked Tickers (for AI extraction)
# ===========================================
TRACKED_TICKERS = [
    # Mega cap tech
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
    # Semiconductors
    "AMD", "INTC", "AVGO", "QCOM", "TSM", "ASML", "MU", "MRVL",
    # AI/Data Centers
    "PLTR", "SNOW", "AI", "PATH", "DDOG",
    # Energy/Utilities
    "VST", "CEG", "NRG", "XEL", "NEE",
    # Nuclear/Uranium
    "CCJ", "UEC", "DNN", "NXE", "SMR",
    # Pharma/Healthcare
    "LLY", "NVO", "PFE", "JNJ", "MRNA", "HIMS",
    # Shipping
    "ZIM", "SBLK", "DAC", "GOGL",
    # Commodities
    "FCX", "SCCO", "RIO", "BHP", "VALE",
    # Retail
    "WMT", "TGT", "COST",
    # China exposure
    "BABA", "JD", "PDD", "NIO", "XPEV",
    # ETFs
    "SPY", "QQQ", "IWM", "XLF", "XLE", "XLK",
    # Crypto / macro proxies (so Polymarket crypto + Fed markets map to tradables)
    "COIN", "MSTR", "MARA", "RIOT", "HOOD", "IBIT", "GBTC", "BITO",
    "GLD", "SLV", "TLT", "USO", "UUP",
]

# ===========================================
# Polymarket question -> ticker mapping
# ===========================================
# Polymarket questions name companies/assets in prose ("Will Bitcoin hit $150k?").
# This maps those phrases to tradable proxies so prediction-market signals carry
# related tickers. Keys are lowercase substrings matched against the question.
QUESTION_TICKER_MAP = {
    "bitcoin": ["IBIT", "COIN", "MSTR"],
    "btc": ["IBIT", "COIN", "MSTR"],
    "ethereum": ["COIN"],
    "eth ": ["COIN"],
    "solana": ["COIN"],
    "crypto": ["COIN", "IBIT"],
    "coinbase": ["COIN"],
    "microstrategy": ["MSTR"],
    "nvidia": ["NVDA"],
    "tesla": ["TSLA"],
    "apple": ["AAPL"],
    "microsoft": ["MSFT"],
    "amazon": ["AMZN"],
    "meta": ["META"],
    "google": ["GOOGL"],
    "alphabet": ["GOOGL"],
    "palantir": ["PLTR"],
    "s&p": ["SPY"],
    "sp500": ["SPY"],
    "s&p 500": ["SPY"],
    "nasdaq": ["QQQ"],
    "recession": ["SPY", "TLT"],
    "rate cut": ["TLT", "SPY"],
    "rate hike": ["TLT"],
    "interest rate": ["TLT"],
    "fed": ["TLT", "SPY"],
    "inflation": ["TLT", "GLD"],
    "cpi": ["TLT", "GLD"],
    "gold": ["GLD"],
    "oil": ["USO", "XLE"],
}
