"""
Tools module providing search and web page scraping capabilities.
"""
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search DuckDuckGo for the query and return relevant search results.

    Args:
        query: The search term or question.
        max_results: Maximum number of links/snippets to fetch (default: 5).

    Returns:
        List of dicts with 'title', 'href', and 'body' snippets.
    """
    results: List[Dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            for item in raw_results:
                results.append({
                    "title": item.get("title", ""),
                    "href": item.get("href", ""),
                    "body": item.get("body", "")
                })
    except Exception as e:
        results.append({
            "title": "Error",
            "href": "",
            "body": f"Failed to execute web search: {str(e)}"
        })
    return results


def scrape_webpage(url: str, max_chars: int = 4000) -> str:
    """
    Scrape text content from a target URL, stripping scripts, styles, and extra whitespace.

    Args:
        url: The web URL to scrape.
        max_chars: Maximum characters to return to prevent excessive context size.

    Returns:
        Cleaned text extract from the webpage.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove irrelevant tags
        for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Extract text content
        lines = (line.strip() for line in soup.get_text().splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        if len(text) > max_chars:
            return text[:max_chars] + f"\n\n... [Content truncated at {max_chars} chars] ..."
        return text if text else "No readable content extracted."
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"
