#!/usr/bin/env python3
"""
LLM Web Summarizer - CLI

A web scraper that uses LLM to extract and summarize information from URLs.
"""
import click
from tqdm import tqdm

from scraper import scrape_url
from llm import summarize_with_llm
from config import load_config, get_summarization_config

@click.command()
@click.argument('url')
@click.option('--max-length', '-m', default=300, help='Maximum summary length in words')
@click.option('--provider', '-p', default='minimax', 
              type=click.Choice(['minimax', 'openai']), help='LLM provider to use')
@click.option('--model', '-M', default=None, help='LLM model to use')
@click.option('--no-summarize', '-n', is_flag=True, help='Only scrape, do not summarize')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(url: str, max_length: int, provider: str, model: str, no_summarize: bool, verbose: bool):
    """
    Scrape and summarize web content using LLM.
    
    URL: The URL to scrape and summarize
    """
    config = load_config()
    
    if verbose:
        click.echo(f"🔍 Scraping: {url}")
    
    # Scrape the URL
    try:
        with tqdm(total=100, desc="Scraping", disable=not verbose) as pbar:
            data = scrape_url(url)
            pbar.update(100)
        
        if verbose:
            click.echo(f"✅ Title: {data['title']}")
            click.echo(f"📄 Content length: {len(data['content'])} chars")
    except Exception as e:
        click.echo(f"❌ Error scraping: {e}", err=True)
        return
    
    if no_summarize:
        click.echo("\n--- Scraped Content ---")
        click.echo(data['content'][:2000])
        if len(data['content']) > 2000:
            click.echo(f"\n... ({len(data['content']) - 2000} more chars)")
        return
    
    # Summarize with LLM
    click.echo(f"\n🤖 Summarizing with {provider}...")
    
    try:
        with tqdm(total=100, desc="Summarizing", disable=not verbose) as pbar:
            summary = summarize_with_llm(
                text=data['content'],
                provider=provider,
                max_length=max_length,
                model=model
            )
            pbar.update(100)
        
        click.echo("\n--- Summary ---")
        click.echo(summary)
        
    except ValueError as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        click.echo("\n💡 To use MiniMax, set MINIMAX_API_KEY environment variable")
        click.echo("💡 To use OpenAI, set OPENAI_API_KEY environment variable")
    except Exception as e:
        click.echo(f"❌ Error summarizing: {e}", err=True)

if __name__ == "__main__":
    main()
