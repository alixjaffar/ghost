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
]
