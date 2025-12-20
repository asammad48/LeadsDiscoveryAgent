from ddgs import DDGS
from bs4 import BeautifulSoup
import requests
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

@register_scraper
class InstagramScraper(BaseScraper):
    """
    Scrapes Instagram by using DuckDuckGo Search to find public profiles,
    then visits each page to extract details.
    """
    platform = "instagram"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        """
        Performs a search for Instagram profiles and scrapes each one.
        """
        print(f"Starting Instagram scrape for query: {query}")
        with DDGS() as ddgs:
            # Search for public Instagram profiles
            search_results = [r for r in ddgs.text(f"site:instagram.com {query}", max_results=10)]

        if not search_results:
            raise NoResultsFoundError(self.platform)

        print(f"Found {len(search_results)} Instagram links. Now scraping individual pages.")
        results = []
        for result in search_results:
            try:
                # Use a session to better mimic a browser
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                response = session.get(result['href'], timeout=10)
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
            print("Could not extract any valid business data from the Instagram links.")
            raise NoResultsFoundError(self.platform)

        return results, None

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        """
        Not used for this scraper as DDGS provides direct links.
        """
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        """
        Parses the HTML of an Instagram profile page.
        Note: Instagram's structure is heavily reliant on JavaScript. This parsing is a best-effort
        approach based on common meta tags.
        """
        business_data = {
            'platform': self.platform,
            'source_url': source_url,
            'business_name': None,
            'description/snippet': None
        }

        # Try to get the profile name from the <title> tag
        if soup.title and soup.title.string:
            # e.g., "Username (@username) • Instagram photos and videos"
            title_parts = soup.title.string.split('•')
            if title_parts:
                business_data['business_name'] = title_parts[0].strip()

        # Try to get the description from the 'description' meta tag
        description_tag = soup.find('meta', attrs={'name': 'description'})
        if description_tag and description_tag.get('content'):
            business_data['description/snippet'] = description_tag['content']

        return business_data
