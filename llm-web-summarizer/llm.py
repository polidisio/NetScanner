"""
LLM integration module for summarization.
"""
import os
from typing import Optional
from config import get_provider_config, get_summarization_config

class LLMSummarizer:
    """Base class for LLM summarization"""
    
    def summarize(self, text: str, max_length: int = 300, prompt: str = None) -> str:
        """Summarize text using LLM - override in subclass"""
        raise NotImplementedError

class MiniMaxSummarizer(LLMSummarizer):
    """MiniMax LLM summarizer"""
    
    def __init__(self, api_key: str = None, model: str = None):
        config = get_provider_config("minimax")
        self.api_key = api_key or config.get("api_key") or os.getenv("MINIMAX_API_KEY")
        self.model = model or config.get("default_model", "MiniMax-M2.5")
        self.base_url = config.get("base_url", "https://api.minimax.chat/v1")
        
        if not self.api_key:
            raise ValueError("MiniMax API key not configured")
    
    def summarize(self, text: str, max_length: int = 300, prompt: str = None) -> str:
        """Summarize text using MiniMax LLM"""
        import requests
        
        summarization_config = get_summarization_config()
        if not prompt:
            prompt = summarization_config.get(
                "default_prompt", 
                "Summarize the following content in {max_length} words or less:"
            ).format(max_length=max_length)
        
        full_prompt = f"{prompt}\n\nContent:\n{text[:8000]}"  # Limit context
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": max_length * 4  # Rough estimate
        }
        
        response = requests.post(
            f"{self.base_url}/text/chatcompletion_v2",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"MiniMax API error: {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]

class OpenAISummarizer(LLMSummarizer):
    """OpenAI LLM summarizer"""
    
    def __init__(self, api_key: str = None, model: str = None):
        config = get_provider_config("openai")
        self.api_key = api_key or config.get("api_key") or os.getenv("OPENAI_API_KEY")
        self.model = model or config.get("default_model", "gpt-4o")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
    
    def summarize(self, text: str, max_length: int = 300, prompt: str = None) -> str:
        """Summarize text using OpenAI LLM"""
        from openai import OpenAI
        
        summarization_config = get_summarization_config()
        if not prompt:
            prompt = summarization_config.get(
                "default_prompt", 
                "Summarize the following content in {max_length} words or less:"
            ).format(max_length=max_length)
        
        client = OpenAI(api_key=self.api_key)
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": f"{prompt}\n\n{text[:8000]}"}
            ],
            temperature=0.7,
            max_tokens=max_length * 4
        )
        
        return response.choices[0].message.content

def get_summarizer(provider: str = "minimax", **kwargs) -> LLMSummarizer:
    """Factory function to get summarizer by provider"""
    if provider == "minimax":
        return MiniMaxSummarizer(**kwargs)
    elif provider == "openai":
        return OpenAISummarizer(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")

def summarize_with_llm(
    text: str, 
    provider: str = "minimax", 
    max_length: int = 300,
    model: str = None,
    prompt: str = None
) -> str:
    """Convenience function to summarize text with LLM"""
    summarizer = get_summarizer(provider=provider, model=model)
    return summarizer.summarize(text, max_length=max_length, prompt=prompt)
