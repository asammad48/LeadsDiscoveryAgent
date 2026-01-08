from ddgs import DDGS
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError
import asyncio

@register_scraper
class InstagramScraper(BaseScraper):
    platform = "instagram"

    async def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        print(f"Starting Instagram scrape for social presence validation: {query}")
        loop = asyncio.get_event_loop()
        search_results = await loop.run_in_executor(None, self._perform_search, query)

        if not search_results:
            raise NoResultsFoundError(self.platform)

        print(f"Found {len(search_results)} potential Instagram pages.")
        results = []
        for result in search_results:
            business_name = self._clean_title(result.get('title', ''))

            results.append({
                'platform': self.platform,
                'business_name': business_name,
                'source_url': result.get('href'),
                'description/snippet': result.get('body'),
            })
            print(f"  > Found social presence for: {business_name}")

        return results, None

    def _perform_search(self, query: str):
        with DDGS() as ddgs:
            return [r for r in ddgs.text(f"site:instagram.com {query}", max_results=10)]

    def _clean_title(self, title: str) -> str:
        if '•' in title:
            return title.split('•')[0].strip()
        return title

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        return {}
