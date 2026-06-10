"""Data models for Social Signal Tracker."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Platform(str, Enum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    REDDIT = "reddit"
    INSTAGRAM = "instagram"


class Sentiment(str, Enum):
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"


class ContentItem(BaseModel):
    """A piece of scraped content from any platform."""
    id: str
    platform: Platform
    author: str
    author_followers: Optional[int] = None
    author_verified: bool = False
    title: Optional[str] = None
    content: str
    url: str
    published_at: datetime
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    engagement: dict = Field(default_factory=dict)  # likes, views, comments, etc.
    raw_data: dict = Field(default_factory=dict)


class TickerMention(BaseModel):
    """A ticker mentioned in content with sentiment analysis."""
    id: str
    content_id: str
    ticker: str
    sentiment: Sentiment
    confidence: float  # 0-1
    context: str  # The sentence/paragraph mentioning the ticker
    price_target: Optional[float] = None
    timeframe: Optional[str] = None  # e.g., "1 week", "end of year"
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class InfluencerProfile(BaseModel):
    """Profile of a tracked influencer."""
    id: str
    platform: Platform
    username: str
    display_name: str
    followers: int
    verified: bool = False
    profile_url: str
    avatar_url: Optional[str] = None
    description: Optional[str] = None
    last_scraped: Optional[datetime] = None
    total_mentions: int = 0
    avg_sentiment_score: float = 0.0


class SignalSummary(BaseModel):
    """Aggregated signal for a ticker."""
    ticker: str
    total_mentions: int
    bullish_count: int
    bearish_count: int
    neutral_count: int
    avg_sentiment: float  # -1 to 1
    sentiment_change_24h: float
    top_influencers: list[str]
    recent_mentions: list[TickerMention]
    price_targets: list[float]
    platforms: dict[str, int]  # Platform -> mention count
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NarrativeShift(BaseModel):
    """Detected narrative shift for a ticker."""
    id: str
    ticker: str
    detected_at: datetime
    previous_sentiment: float
    current_sentiment: float
    shift_magnitude: float
    trigger_content: list[str]  # IDs of content that triggered the shift
    description: str
