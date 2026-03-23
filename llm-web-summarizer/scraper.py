"""
Web scraper module for extracting content from URLs.
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional
from config import get_scraper_config

class WebScraper:
    """Web scraper for extracting content from URLs"""
    
    def __init__(self, timeout: int = None, max_retries: int = None):
        config = get_scraper_config()
        self.timeout = timeout or config.get("timeout", 30)
        self.max_retries = max_retries or config.get("max_retries", 3)
        self.user_agent = config.get("user_agent", "LLM-Web-Summarizer/1.0")
    
    def fetch(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL"""
        headers = {
            "User-Agent": self.user_agent
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to fetch {url}: {e}")
                continue
        
        return None
    
    def extract_text(self, html: str) -> str:
        """Extract main text content from HTML"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find main content
        main_content = (
            soup.find("main") or 
            soup.find("article") or 
            soup.find("div", class_=lambda x: x and "content" in x.lower()) or
            soup.find("div", class_=lambda x: x and "article" in x.lower()) or
            soup.body
        )
        
        if main_content:
            # Get text and clean it up
            text = main_content.get_text(separator='\n')
            lines = [line.strip() for line in text.split('\n')]
            text = '\n'.join(line for line in lines if line)
            return text
        
        return soup.get_text(separator='\n')
    
    def extract_title(self, html: str) -> str:
        """Extract page title"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Try different ways to get the title
        if soup.title:
            return soup.title.string
        
        h1 = soup.find("h1")
        if h1:
            return h1.get_text()
        
        return "Untitled"
    
    def scrape(self, url: str) -> dict:
        """Scrape URL and return structured data"""
        html = self.fetch(url)
        if not html:
            raise Exception(f"Could not fetch {url}")
        
        return {
            "url": url,
            "title": self.extract_title(html),
            "content": self.extract_text(html)
        }

def scrape_url(url: str) -> dict:
    """Convenience function to scrape a URL"""
    scraper = WebScraper()
    return scraper.scrape(url)
