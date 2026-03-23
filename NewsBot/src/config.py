"""Configuration for NewsBot."""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Bot configuration."""
    
    # Telegram
    telegram_token: str
    
    # MiniMax API
    minimax_api_key: Optional[str] = None
    minimax_base_url: str = "https://api.minimax.chat/v1"
    minimax_model: str = "MiniMax-M2.5"
    
    # News sources per topic
    news_sources: dict = None
    
    def __post_init__(self):
        if self.news_sources is None:
            self.news_sources = {
                "cycling": [
                    "https://www.cyclingnews.com",
                    "https://www.bikeradar.com",
                    "https://zwiftinsider.com"
                ],
                "ai": [
                    "https://venturebeat.com/category/ai/",
                    "https://techcrunch.com/category/artificial-intelligence/"
                ],
                "ios": [
                    "https://www.swift.org/blog/",
                    "https://www.hackingwithswift.com"
                ],
                "gaming": [
                    "https://ign.com",
                    "https://www.gamespot.com"
                ],
                "cybersecurity": [
                    "https://thehackernews.com",
                    "https://krebsonsecurity.com",
                    "https://www.darkreading.com"
                ]
            }
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment variables."""
        return cls(
            telegram_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            minimax_api_key=os.getenv("MINIMAX_API_KEY"),
            minimax_base_url=os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1"),
            minimax_model=os.getenv("MINIMAX_MODEL", "MiniMax-M2.5")
        )
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.telegram_token:
            return False
        return True
