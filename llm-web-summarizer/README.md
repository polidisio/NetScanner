# LLM Web Summarizer

A web scraper that uses LLM to extract and summarize information from URLs. Built with Python, uses BeautifulSoup for scraping and MiniMax LLM for intelligent summarization.

## Features

- Extract main content from any URL
- Intelligent summarization using LLM
- Configurable extraction (titles, paragraphs, key info)
- Support for multiple LLM providers (MiniMax, OpenAI)
- Command-line interface

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### CLI

```bash
python main.py "https://example.com"
python main.py "https://news.ycombinator.com" --max-length 500
```

### Python

```python
from scraper import summarize_url

result = summarize_url(
    url="https://example.com",
    max_length=300,
    provider="minimax",
    model="MiniMax-M2.5"
)
print(result)
```

## Configuration

Edit `config.yaml` to set your API keys and preferences.

## License

MIT
