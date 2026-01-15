"""
Module for scraping job descriptions from web URLs
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional
import config


def scrape_job_description(url: str) -> Optional[str]:
    """
    Scrape job description from the given URL
    Returns the text content of the page, or None if scraping fails
    """
    try:
        headers = {
            'User-Agent': config.USER_AGENT
        }

        response = requests.get(url, headers=headers, timeout=config.SCRAPING_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up text - break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None


def clean_job_description(text: str) -> str:
    """
    Clean and format job description text
    """
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)
