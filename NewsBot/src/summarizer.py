"""LLM summarizer module."""
import requests
from typing import Optional

class Summarizer:
    """Summarizes text using LLM."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.minimax.chat/v1", model: str = "MiniMax-M2.5"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
    
    def summarize(self, text: str, max_length: int = 100) -> str:
        """Summarize text using MiniMax LLM."""
        if not self.api_key:
            # Return truncated text if no API key
            return text[:max_length * 4] + "..."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"Summarize the following in {max_length} words or less:\n\n{text[:4000]}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": max_length * 4
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/text/chatcompletion_v2",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def summarize_batch(self, texts: list, max_length: int = 50) -> list:
        """Summarize multiple texts."""
        return [self.summarize(text, max_length) for text in texts]
