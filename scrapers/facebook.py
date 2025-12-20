from ddgs import DDGS
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

@register_scraper
class FacebookScraper(BaseScraper):
    """
    Scrapes Facebook by using DuckDuckGo Search to find public business pages.
    Directly scraping Facebook is often blocked, so this approach extracts data
    from search result snippets.
    """
    platform = "facebook"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        """
        Performs a search for Facebook pages and extracts data from the results.
        """
        print(f"Starting Facebook scrape for query: {query}")
        with DDGS() as ddgs:
            # Search for public Facebook pages related to the query
            search_results = [r for r in ddgs.text(f"site:facebook.com {query}", max_results=10)]

        if not search_results:
            raise NoResultsFoundError(self.platform)

        print(f"Found {len(search_results)} Facebook links. Extracting data from snippets.")
        results = []
        for result in search_results:
            # For Facebook, we extract data from the search result snippet
            # as visiting the page directly is unreliable.
            business_name = result['title'].replace(" - Facebook", "").strip()

            results.append({
                'business_name': business_name,
                'description/snippet': result['body'],
                'platform': self.platform,
                'source_url': result['href'],
                'website': None,
                'phone': None,
                'address': None
            })
            print(f"  > Extracted: {business_name}")

        return results, None

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        """
        Not used for this scraper as DDGS provides direct links.
        """
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        """
        Direct parsing of Facebook pages is not implemented due to high likelihood of being blocked.
        Data is extracted from search engine snippets instead.
        """
        return {}
