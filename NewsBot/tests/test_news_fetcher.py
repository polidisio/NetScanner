"""Tests for news_fetcher module."""
import pytest
from unittest.mock import Mock, patch
from src.news_fetcher import NewsFetcher, NewsItem

class TestNewsFetcher:
    """Tests for NewsFetcher class."""
    
    def test_fetcher_initialization(self):
        """Test fetcher initializes with default timeout."""
        fetcher = NewsFetcher()
        assert fetcher.timeout == 30
        assert fetcher.user_agent == "NewsBot/1.0"
    
    def test_fetcher_custom_timeout(self):
        """Test fetcher with custom timeout."""
        fetcher = NewsFetcher(timeout=60)
        assert fetcher.timeout == 60
    
    def test_fetch_returns_none_on_error(self):
        """Test fetch returns None on network error."""
        fetcher = NewsFetcher()
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            result = fetcher.fetch("https://example.com")
            assert result is None
    
    def test_extract_headlines_from_article_tags(self):
        """Test headline extraction from article tags."""
        html = """
        <html>
        <body>
            <article>
                <h2><a href="/news/1">First News Title</a></h2>
            </article>
            <article>
                <h3>Second News Title</h3>
            </article>
        </body>
        </html>
        """
        fetcher = NewsFetcher()
        items = fetcher.extract_headlines(html, "https://example.com")
        
        assert len(items) == 2
        assert items[0].title == "First News Title"
        assert items[0].url == "/news/1"
        assert items[1].title == "Second News Title"
    
    def test_extract_headlines_limit(self):
        """Test headline extraction respects max_items."""
        html = """
        <html><body>
        """ + "".join([
            f'<article><h2><a href="/news/{i}">Title {i}</a></h2></article>'
            for i in range(10)
        ]) + """
        </body></html>
        """
        fetcher = NewsFetcher()
        items = fetcher.extract_headlines(html, "https://example.com", max_items=3)
        
        assert len(items) == 3
    
    def test_extract_headlines_empty_html(self):
        """Test extraction from HTML with no articles."""
        html = "<html><body><p>No news here</p></body></html>"
        fetcher = NewsFetcher()
        items = fetcher.extract_headlines(html, "https://example.com")
        
        # Falls back to link extraction, may have items or not
        assert isinstance(items, list)
    
    def test_format_news_empty(self):
        """Test formatting empty news list."""
        fetcher = NewsFetcher()
        result = fetcher.format_news([])
        assert "No news found" in result
    
    def test_format_news_single_item(self):
        """Test formatting single news item."""
        fetcher = NewsFetcher()
        items = [NewsItem(
            title="Test News",
            url="https://example.com/news",
            source="https://example.com"
        )]
        result = fetcher.format_news(items)
        
        assert "Test News" in result
        assert "https://example.com/news" in result

class TestNewsItem:
    """Tests for NewsItem dataclass."""
    
    def test_news_item_creation(self):
        """Test NewsItem with all fields."""
        item = NewsItem(
            title="Test Title",
            url="https://example.com",
            source="example.com",
            published="2024-01-01",
            summary="A summary"
        )
        
        assert item.title == "Test Title"
        assert item.url == "https://example.com"
        assert item.source == "example.com"
        assert item.published == "2024-01-01"
        assert item.summary == "A summary"
    
    def test_news_item_optional_fields(self):
        """Test NewsItem with only required fields."""
        item = NewsItem(
            title="Test",
            url="https://test.com",
            source="test.com"
        )
        
        assert item.title == "Test"
        assert item.published is None
        assert item.summary is None
