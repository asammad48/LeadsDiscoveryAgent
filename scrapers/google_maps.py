from bs4 import BeautifulSoup
import re
import requests
from ddgs import DDGS
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

@register_scraper
class GoogleMapsScraper(BaseScraper):
    """
    Scrapes Google Maps by using DuckDuckGo Search to find Maps URLs, then visits
    each URL to parse business data.
    """
    platform = "google_maps"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        """
        Performs a search for Google Maps links and then scrapes each page.
        """
        print(f"Starting Google Maps scrape for query: {query}")
        with DDGS() as ddgs:
            # Focus search on Google Maps pages
            search_results = [r for r in ddgs.text(f"site:google.com/maps {query}", max_results=15)]

        if not search_results:
            raise NoResultsFoundError(self.platform)

        print(f"Found {len(search_results)} Google Maps links. Now scraping individual pages.")
        results = []
        for result in search_results:
            try:
                response = requests.get(result['href'], timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                business_data = self._parse_profile_page(soup, result['href'])

                if business_data.get("business_name") and business_data["business_name"] != "N/A":
                    results.append(business_data)
                    print(f"  > Successfully scraped: {business_data['business_name']}")
                else:
                    print(f"  > Could not find a valid business name at {result['href']}")

            except requests.RequestException as e:
                print(f"  > Could not fetch URL {result['href']}: {e}")
            except Exception as e:
                print(f"  > An unexpected error occurred while parsing {result['href']}: {e}")

        if not results:
            print("Could not extract any valid business data from the Google Maps links.")
            raise NoResultsFoundError(self.platform)

        return results, None

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        """
        Not used for this scraper as DDGS provides direct links.
        """
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        """
        Parses the HTML of a Google Maps page to extract business information.
        Note: Google Maps pages are heavily JS-driven, so direct HTML parsing is limited.
        """
        business_data = {
            'platform': self.platform,
            'source_url': source_url,
            'business_name': "N/A",
            'phone': None,
            'address': None,
            'website': None
        }

        # Attempt to get the business name from the page title
        if soup.title and soup.title.string:
            business_name_match = re.search(r'^(.*?) - Google Maps', soup.title.string)
            if business_name_match:
                business_data['business_name'] = business_name_match.group(1).strip()

        # Attempt to find a phone number using regex
        # This is a very broad search and may yield false positives
        phone_match = re.search(r'(\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', soup.get_text())
        if phone_match:
            business_data['phone'] = phone_match.group(0)

        return business_data
