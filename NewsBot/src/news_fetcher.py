"""News fetcher module."""
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class NewsItem:
    """Represents a news item."""
    title: str
    url: str
    source: str
    published: Optional[str] = None
    summary: Optional[str] = None

class NewsFetcher:
    """Fetches news from various sources."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.user_agent = "NewsBot/1.0"
    
    def fetch(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL."""
        headers = {"User-Agent": self.user_agent}
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return None
    
    def extract_headlines(self, html: str, source: str, max_items: int = 5) -> List[NewsItem]:
        """Extract headlines from HTML."""
        soup = BeautifulSoup(html, 'lxml')
        items = []
        
        # Try common patterns for news sites
        for article in soup.find_all('article')[:max_items]:
            title_elem = article.find(['h2', 'h3', 'h4']) or article.find('a')
            if title_elem and title_elem.get_text(strip=True):
                link = article.find('a', href=True)
                items.append(NewsItem(
                    title=title_elem.get_text(strip=True),
                    url=link['href'] if link else source,
                    source=source
                ))
        
        # Fallback: look for links with common news patterns
        if not items:
            for a in soup.find_all('a', href=True)[:max_items]:
                text = a.get_text(strip=True)
                if len(text) > 30 and len(text) < 200:
                    items.append(NewsItem(
                        title=text,
                        url=a['href'],
                        source=source
                    ))
        
        return items[:max_items]
    
    def fetch_topic(self, sources: List[str], topic: str) -> List[NewsItem]:
        """Fetch news for a topic from multiple sources."""
        all_items = []
        for source_url in sources:
            html = self.fetch(source_url)
            if html:
                items = self.extract_headlines(html, source_url)
                for item in items:
                    item.source = source_url  # Normalize source
                all_items.extend(items)
        return all_items
    
    def format_news(self, items: List[NewsItem]) -> str:
        """Format news items for display."""
        if not items:
            return "No news found 😕"
        
        lines = ["📰 *Latest News*\n"]
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. [{item.title}]({item.url})")
            lines.append("")
        
        return "\n".join(lines)
