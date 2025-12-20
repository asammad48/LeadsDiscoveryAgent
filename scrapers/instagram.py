from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

@register_scraper
class InstagramScraper(BaseScraper):
    platform = "instagram"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        with DDGS() as ddgs:
            search_results = [r for r in ddgs.text(f"site:instagram.com {query}", max_results=10)]

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
                'social_url': result['href'],
                'source_url': result['href'],
            })

        return results, None

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        business_name = soup.find('title').get_text(strip=True) if soup.find('title') else "N/A"

        return {
            'business_name': business_name,
            'platform': self.platform,
            'social_url': source_url,
            'source_url': source_url,
        }
