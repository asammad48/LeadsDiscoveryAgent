from ddgs import DDGS
from bs4 import BeautifulSoup
import requests
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

@register_scraper
class LinkedInScraper(BaseScraper):
    """
    Scrapes LinkedIn by using DuckDuckGo Search to find public company pages,
    then visits each page to extract details.
    """
    platform = "linkedin"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        """
        Performs a search for LinkedIn company pages and scrapes each one.
        """
        print(f"Starting LinkedIn scrape for query: {query}")
        with DDGS() as ddgs:
            # Search for public LinkedIn company pages
            search_results = [r for r in ddgs.text(f"site:linkedin.com/company {query}", max_results=10)]

        if not search_results:
            raise NoResultsFoundError(self.platform)

        print(f"Found {len(search_results)} LinkedIn company pages. Now scraping individual pages.")
        results = []
        for result in search_results:
            try:
                response = requests.get(result['href'], timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                business_data = self._parse_profile_page(soup, result['href'])

                if business_data.get("business_name"):
                    results.append(business_data)
                    print(f"  > Successfully scraped: {business_data['business_name']}")
                else:
                    print(f"  > Could not find a business name at {result['href']}")

            except requests.RequestException as e:
                print(f"  > Could not fetch URL {result['href']}: {e}")
            except Exception as e:
                print(f"  > An unexpected error occurred while parsing {result['href']}: {e}")

        if not results:
            print("Could not extract any valid business data from the LinkedIn links.")
            raise NoResultsFoundError(self.platform)

        return results, None

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        """
        Not used for this scraper as DDGS provides direct links.
        """
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        """
        Parses the HTML of a LinkedIn company page.
        Note: LinkedIn pages can be hard to parse; this is a best-effort implementation.
        """
        business_data = {
            'platform': self.platform,
            'source_url': source_url,
            'business_name': None,
            'website': None,
            'phone': None,
            'address': None
        }

        # Extract business name from the page title
        if soup.title and soup.title.string:
            business_data['business_name'] = soup.title.string.replace(" | LinkedIn", "").strip()

        return business_data
