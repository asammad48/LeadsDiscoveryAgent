from ddgs import DDGS
from bs4 import BeautifulSoup
import re
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError
import asyncio

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
    platform = "google_search"

    async def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        print(f"Starting discovery scrape on Google Search for query: {query}")
        loop = asyncio.get_event_loop()
        search_results = await loop.run_in_executor(None, self._perform_search, query)

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
            raise NoResultsFoundError(self.platform)

        return results, None

    def _perform_search(self, query: str):
        with DDGS() as ddgs:
            return [r for r in ddgs.text(query, max_results=20)]

    def _is_excluded(self, url: str) -> bool:
        try:
            domain = re.search(r'https?://(?:www\.)?([^/]+)', url).group(1)
            return any(excluded in domain for excluded in EXCLUDED_DOMAINS)
        except (AttributeError, TypeError):
            return True

    def _extract_business_name(self, title: str) -> str:
        suffixes = [' | Home', ' - Official Website', ' | Official Site']
        for suffix in suffixes:
            if suffix in title:
                title = title.split(suffix)[0]
        return title.strip()

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        return {}
