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
    Scrapes Google Maps authoritatively for core business data (website, phone, address).
    Uses DuckDuckGo Search to find Maps URLs, then visits each URL to parse data.
    """
    platform = "google_maps"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        print(f"Starting authoritative Google Maps scrape for query: {query}")
        with DDGS() as ddgs:
            # The ddgs library is used for discovery of place URLs.
            search_results = [r for r in ddgs.text(f"site:google.com/maps/place/ {query}", max_results=15)]

        if not search_results:
            raise NoResultsFoundError(self.platform)

        print(f"Found {len(search_results)} potential Google Maps places. Now parsing for authoritative data.")
        results = []
        for result in search_results:
            # Filter out non-place URLs
            if "/maps/place/" not in result['href']:
                print(f"  > Skipping non-place URL: {result['href']}")
                continue

            try:
                response = requests.get(result['href'], timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                business_data = self._parse_profile_page(soup, result['href'])

                # A valid entry must have a business name.
                if business_data.get("business_name"):
                    results.append(business_data)
                    print(f"  > Successfully extracted authoritative data for: {business_data['business_name']}")
                else:
                    print(f"  > Could not find a valid business name at {result['href']}")

            except requests.RequestException as e:
                print(f"  > Could not fetch URL {result['href']}: {e}")
            except Exception as e:
                print(f"  > An unexpected error occurred while parsing {result['href']}: {e}")

        if not results:
            print("Could not extract any valid business data from Google Maps.")
            raise NoResultsFoundError(self.platform)

        return results, None

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        """
        Parses the HTML of a Google Maps place page to extract authoritative data.
        This uses specific, attribute-based selectors for robustness.
        """
        business_data = {
            'platform': self.platform,
            'source_url': source_url,
            'business_name': None,
            'website': None,
            'phone': None,
            'address': None,
        }

        # --- Authoritative Data Extraction ---

        # Business Name (from H1 tag for main title)
        name_tag = soup.find('h1', class_=re.compile(r'DUwDvf'))
        if name_tag:
            business_data['business_name'] = name_tag.get_text(strip=True)

        # Address (identified by the 'Address' aria-label)
        address_tag = soup.find('button', {'aria-label': re.compile(r'^Address: ')})
        if address_tag:
            business_data['address'] = address_tag['aria-label'].replace('Address: ', '').strip()

        # Website (identified by the 'Website' aria-label)
        website_tag = soup.find('a', {'aria-label': re.compile(r'^Website: ')})
        if website_tag:
            business_data['website'] = website_tag.get('href', None)

        # Phone (identified by the 'phone' aria-label)
        phone_tag = soup.find('a', {'aria-label': re.compile(r'^Phone: ')})
        if phone_tag:
            business_data['phone'] = phone_tag['aria-label'].replace('Phone: ', '').strip()

        return business_data
