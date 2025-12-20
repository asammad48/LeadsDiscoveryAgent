from ddgs import DDGS
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

@register_scraper
class InstagramScraper(BaseScraper):
    """
    Scrapes Instagram for social presence validation.
    Extracts only business name, source URL, and a snippet/bio.
    """
    platform = "instagram"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        print(f"Starting Instagram scrape for social presence validation: {query}")
        with DDGS() as ddgs:
            search_results = [r for r in ddgs.text(f"site:instagram.com {query}", max_results=10)]

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

    def _clean_title(self, title: str) -> str:
        """Removes common suffixes from Instagram page titles."""
        # e.g., "Username (@username) • Instagram photos and videos"
        if '•' in title:
            return title.split('•')[0].strip()
        return title

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        # This scraper does not visit pages.
        return {}
