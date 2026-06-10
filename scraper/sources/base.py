"""Base class for all data sources."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterator
import hashlib


class ContentItem:
    """Standardized content item from any source."""
    
    def __init__(
        self,
        source: str,
        source_id: str,
        title: str,
        content: str,
        url: str,
        author: str = "",
        author_followers: int = 0,
        engagement: int = 0,
        published_at: datetime = None,
        metadata: dict = None,
    ):
        self.source = source
        self.source_id = source_id
        self.title = title
        self.content = content
        self.url = url
        self.author = author
        self.author_followers = author_followers
        self.engagement = engagement
        self.published_at = published_at or datetime.utcnow()
        self.metadata = metadata or {}
        
        # Generate unique ID
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique content ID."""
        unique_str = f"{self.source}:{self.source_id}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "platform": self.source,
            "source_id": self.source_id,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "author": self.author,
            "author_followers": self.author_followers,
            "engagement": self.engagement,
            "created_at": self.published_at.isoformat(),
            "metadata": self.metadata,
        }


class BaseSource(ABC):
    """Abstract base class for data sources."""
    
    name: str = "base"
    
    @abstractmethod
    async def fetch(self, limit: int = 50) -> AsyncIterator[ContentItem]:
        """Fetch content from the source."""
        pass
    
    @abstractmethod
    async def is_configured(self) -> bool:
        """Check if the source is properly configured."""
        pass
