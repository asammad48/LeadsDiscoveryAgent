from ddgs import DDGS
from bs4 import BeautifulSoup
import requests
import re
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

# Domains to be excluded from discovery results
EXCLUDED_DOMAINS = [
    'facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com',
    'youtube.com', 'tiktok.com',
    'booking.com', 'tripadvisor.com', 'kayak.com', 'expedia.com', 'hotels.com',
    'en.wikipedia.org',
    'yelp.com', 'foursquare.com',
    'apps.apple.com', 'play.google.com'
]

@register_scraper
class GoogleSearchScraper(BaseScraper):
    """
    Scrapes Google search for pure discovery of potential business websites.
    It is heavily filtered to exclude aggregators, social media, and booking sites.
    """
    platform = "google_search"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        print(f"Starting discovery scrape on Google Search for query: {query}")
        with DDGS() as ddgs:
            search_results = [r for r in ddgs.text(query, max_results=20)]

        if not search_results:
            raise NoResultsFoundError(self.platform)

        print(f"Found {len(search_results)} potential leads. Now filtering for high-quality results.")
        results = []
        for result in search_results:
            source_url = result.get('href')
            if not source_url or self._is_excluded(source_url):
                continue

            business_name = self._extract_business_name(result.get('title', ''))

            results.append({
                'platform': self.platform,
                'business_name': business_name,
                'source_url': source_url
            })
            print(f"  > Discovered potential lead: {business_name}")

        if not results:
            print("No high-quality, direct business websites found after filtering.")
            raise NoResultsFoundError(self.platform)

        return results, None

    def _is_excluded(self, url: str) -> bool:
        """Checks if a URL belongs to an excluded domain."""
        try:
            domain = re.search(r'https?://(?:www\.)?([^/]+)', url).group(1)
            return any(excluded in domain for excluded in EXCLUDED_DOMAINS)
        except (AttributeError, TypeError):
            return True # Exclude if URL is malformed

    def _extract_business_name(self, title: str) -> str:
        """A simple utility to clean up the page title for use as a business name."""
        # Remove common suffixes
        suffixes = [' | Home', ' - Official Website', ' | Official Site']
        for suffix in suffixes:
            if suffix in title:
                title = title.split(suffix)[0]
        return title.strip()

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        # This scraper no longer visits pages, so this is not used.
        return {}
