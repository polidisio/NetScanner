"""
Configuration loader for LLM Web Summarizer.
"""
import os
import yaml
from pathlib import Path

CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / "config.yaml"

_default_config = {
    "default_provider": "minimax",
    "minimax": {
        "api_key": "",
        "base_url": "https://api.minimax.chat/v1",
        "default_model": "MiniMax-M2.5"
    },
    "scraper": {
        "timeout": 30,
        "max_retries": 3,
        "user_agent": "LLM-Web-Summarizer/1.0"
    },
    "summarization": {
        "default_max_length": 300,
        "default_prompt": "Summarize the following web content in {max_length} words or less, focusing on the key information:"
    }
}

_config = None

def load_config() -> dict:
    """Load configuration from config.yaml"""
    global _config
    
    if _config is not None:
        return _config
    
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            user_config = yaml.safe_load(f) or {}
            _config = {**_default_config, **user_config}
    else:
        _config = _default_config.copy()
    
    # Override with environment variables
    if os.getenv("MINIMAX_API_KEY"):
        _config["minimax"]["api_key"] = os.getenv("MINIMAX_API_KEY")
    if os.getenv("OPENAI_API_KEY"):
        _config["openai"]["api_key"] = os.getenv("OPENAI_API_KEY")
    
    return _config

def get_provider_config(provider: str = None) -> dict:
    """Get configuration for a specific provider"""
    config = load_config()
    provider = provider or config.get("default_provider", "minimax")
    return config.get(provider, {})

def get_scraper_config() -> dict:
    """Get scraper configuration"""
    config = load_config()
    return config.get("scraper", {})

def get_summarization_config() -> dict:
    """Get summarization configuration"""
    config = load_config()
    return config.get("summarization", {})
