"""
Module for scraping job descriptions from web URLs
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional
import config


def scrape_job_description(url: str) -> Optional[str]:
    """
    Scrape job description from the given URL with improved patience and extraction
    Returns the text content of the page, or None if scraping fails
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        # Increase timeout to 30 seconds for better patience
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "form", "button"]):
            element.decompose()

        # Try to find job description in common containers first
        job_description = None

        # Common selectors for job descriptions
        selectors = [
            {'class': 'job-description'},
            {'class': 'description'},
            {'class': 'job-details'},
            {'class': 'job_description'},
            {'class': 'jobDescription'},
            {'id': 'job-description'},
            {'id': 'description'},
            {'role': 'main'},
            {'class': 'content'},
            {'class': 'main-content'}
        ]

        for selector in selectors:
            element = soup.find(['div', 'section', 'article', 'main'], selector)
            if element:
                job_description = element.get_text(separator='\n', strip=True)
                break

        # Fallback to entire body if nothing found
        if not job_description or len(job_description) < 100:
            # Get main content area
            main = soup.find('main') or soup.find('article') or soup.find('body')
            if main:
                job_description = main.get_text(separator='\n', strip=True)

        if not job_description:
            job_description = soup.get_text(separator='\n', strip=True)

        # Clean up text
        lines = []
        for line in job_description.split('\n'):
            cleaned = line.strip()
            # Skip very short lines (likely navigation/menu items)
            if len(cleaned) > 3:
                lines.append(cleaned)

        # Remove duplicate consecutive lines
        final_lines = []
        prev_line = None
        for line in lines:
            if line != prev_line:
                final_lines.append(line)
                prev_line = line

        text = '\n'.join(final_lines)

        # Only return if we got substantial content
        if len(text) > 200:  # At least 200 characters
            return text
        else:
            print(f"Scraped content too short ({len(text)} chars), might not be job description")
            return None

    except requests.Timeout:
        print(f"Timeout error scraping {url} - site took too long to respond")
        return None
    except requests.RequestException as e:
        print(f"Request error scraping {url}: {str(e)}")
        return None
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
