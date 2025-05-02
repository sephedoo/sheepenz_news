"""
NewsItem data model.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class NewsItem:
    """Data class to represent a news item"""
    title: str
    summary: str
    source: str
    url: Optional[str] = None
    published_date: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    local_image_path: Optional[str] = None
    slug: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the NewsItem to a dictionary"""
        return {
            "title": self.title,
            "summary": self.summary,
            "source": self.source,
            "url": self.url,
            "published_date": self.published_date,
            "category": self.category,
            "image_url": self.image_url,
            "slug": self.slug
        }