from bs4 import BeautifulSoup
import re
from duckduckgo_search import DDGS
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

@register_scraper
class GoogleMapsScraper(BaseScraper):
    platform = "google_maps"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        with DDGS() as ddgs:
            search_results = [r for r in ddgs.text(f"site:google.com/maps {query}", max_results=10)]

        if not search_results:
            raise NoResultsFoundError(self.platform)

        results = []
        for result in search_results:
            business_name = result['title']
            description = result['body']

            results.append({
                'business_name': business_name,
                'platform': self.platform,
                'description/snippet': description,
                'source_url': result['href'],
            })

        return results, None

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        business_name_match = re.search(r'"(.*?)"', soup.title.string) if soup.title else None
        business_name = business_name_match.group(1) if business_name_match else "N/A"
        phone_match = re.search(r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', soup.get_text())
        phone = phone_match.group(0) if phone_match else None

        return {
            'business_name': business_name,
            'platform': self.platform,
            'phone': phone,
            'source_url': source_url,
        }
