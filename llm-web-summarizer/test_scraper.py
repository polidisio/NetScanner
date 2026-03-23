"""
Unit tests for the scraper module.
"""
import pytest
from unittest.mock import Mock, patch
from scraper import WebScraper, scrape_url

class TestWebScraper:
    """Tests for WebScraper class"""
    
    def test_extract_title_from_html(self):
        """Test title extraction from simple HTML"""
        scraper = WebScraper()
        html = "<html><head><title>Test Page</title></head><body></body></html>"
        title = scraper.extract_title(html)
        assert title == "Test Page"
    
    def test_extract_text_removes_scripts(self):
        """Test that script and style elements are removed"""
        scraper = WebScraper()
        html = """
        <html>
            <script>alert('test');</script>
            <style>body { color: red; }</style>
            <body><p>Main content</p></body>
        </html>
        """
        text = scraper.extract_text(html)
        assert "alert" not in text
        assert "color" not in text
        assert "Main content" in text
    
    def test_extract_text_preserves_paragraphs(self):
        """Test that paragraph content is preserved"""
        scraper = WebScraper()
        html = """
        <html><body>
            <p>First paragraph</p>
            <p>Second paragraph</p>
        </body></html>
        """
        text = scraper.extract_text(html)
        assert "First paragraph" in text
        assert "Second paragraph" in text
    
    def test_scrape_url_returns_dict(self):
        """Test that scrape_url returns expected structure"""
        with patch('scraper.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html><head><title>Test</title></head><body><p>Content</p></body></html>"
            mock_get.return_value = mock_response
            
            result = scrape_url("https://example.com")
            
            assert isinstance(result, dict)
            assert "url" in result
            assert "title" in result
            assert "content" in result
            assert result["url"] == "https://example.com"
    
    def test_scrape_url_handles_timeout(self):
        """Test that scraper respects timeout setting"""
        scraper = WebScraper(timeout=10)
        assert scraper.timeout == 10
    
    def test_extract_title_fallback_to_h1(self):
        """Test title extraction falls back to h1 if no title tag"""
        scraper = WebScraper()
        html = "<html><body><h1>Header Title</h1></body></html>"
        title = scraper.extract_title(html)
        assert title == "Header Title"
    
    def test_extract_title_fallback_to_untitled(self):
        """Test title extraction returns Untitled when no title found"""
        scraper = WebScraper()
        html = "<html><body><p>No title here</p></body></html>"
        title = scraper.extract_title(html)
        assert title == "Untitled"


class TestScraperIntegration:
    """Integration tests (require network)"""
    
    @pytest.mark.integration
    def test_scrape_example_com(self):
        """Test scraping example.com (requires network)"""
        result = scrape_url("https://example.com")
        assert result["url"] == "https://example.com"
        assert len(result["content"]) > 0
        assert result["title"] == "Example Domain"
