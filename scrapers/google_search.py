from duckduckgo_search import DDGS
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

@register_scraper
class GoogleSearchScraper(BaseScraper):
    platform = "google_search"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        with DDGS() as ddgs:
            search_results = [r for r in ddgs.text(query, max_results=10)]

        if not search_results:
            raise NoResultsFoundError(self.platform)

        results = []
        for result in search_results:
            results.append({
                'business_name': result['title'],
                'description/snippet': result['body'],
                'platform': self.platform,
                'source_url': result['href'],
            })

        # DuckDuckGo Search library doesn't support pagination directly
        return results, None

    def _parse_search_results(self, soup):
        # This method is no longer used
        return []

    def _parse_profile_page(self, soup, source_url):
        # This method is no longer used
        return {}
