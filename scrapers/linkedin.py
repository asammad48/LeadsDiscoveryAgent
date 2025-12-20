from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError
from utils.http_client import http_client

@register_scraper
class LinkedInScraper(BaseScraper):
    platform = "linkedin"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        with DDGS() as ddgs:
            # Use DuckDuckGo to find company profile pages on LinkedIn
            search_results = [r for r in ddgs.text(f"site:linkedin.com/company {query}", max_results=5)]

        if not search_results:
            raise NoResultsFoundError(self.platform)

        results = []
        for result in search_results:
            profile_url = result['href']
            # We have the profile URL, but fetching and parsing the full page is often blocked.
            # For this fix, we will extract what we can from the search result itself.
            results.append({
                'business_name': result['title'].replace(" | LinkedIn", ""),
                'description/snippet': result['body'],
                'platform': self.platform,
                'source_url': profile_url,
            })

        return results, None

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        # No longer used
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        # Parsing the live profile page is unreliable, so we extract from search results instead.
        # This function can be kept for future enhancements if direct fetching becomes possible.
        return {}
