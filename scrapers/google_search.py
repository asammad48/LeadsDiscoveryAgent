from ddgs import DDGS
from bs4 import BeautifulSoup
import requests
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

@register_scraper
class GoogleSearchScraper(BaseScraper):
    """
    Scrapes Google search results using DuckDuckGo Search as a proxy to avoid blocks.
    It first gets search result links and then visits each link to extract business data.
    """
    platform = "google_search"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        """
        Performs a search and then scrapes each result page for details.
        """
        print(f"Starting Google Search scrape for query: {query}")
        with DDGS() as ddgs:
            # Fetch more results to increase chances of finding valid business pages
            search_results = [r for r in ddgs.text(query, max_results=20)]

        if not search_results:
            raise NoResultsFoundError(self.platform)

        print(f"Found {len(search_results)} search results. Now scraping individual pages.")
        results = []
        for result in search_results:
            try:
                # Visit the URL to get the page content
                response = requests.get(result['href'], timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Basic parsing logic to find business details
                business_data = self._parse_profile_page(soup, result['href'])

                # Ensure we have at least a name before adding
                if business_data.get("business_name"):
                    results.append(business_data)
                    print(f"  > Successfully scraped: {business_data['business_name']}")
                else:
                    print(f"  > Could not find business name at {result['href']}")

            except requests.RequestException as e:
                print(f"  > Could not fetch URL {result['href']}: {e}")
            except Exception as e:
                print(f"  > An unexpected error occurred while parsing {result['href']}: {e}")

        if not results:
            print("Could not extract any valid business data from the search results.")
            raise NoResultsFoundError(self.platform)

        return results, None

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        """
        Not used for this scraper because the DDGS library returns direct links,
        so there is no search results page to parse.
        """
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        """
        Parses the HTML of a business page to extract key information.
        This is a basic implementation and could be made more robust.
        """
        business_data = {'source_url': source_url, 'platform': self.platform}

        # Try to find the business name from the <title> tag as a fallback
        if soup.title:
            business_data['business_name'] = soup.title.string.split('|')[0].strip()
        else:
            business_data['business_name'] = "No title found"

        # This is a placeholder for more sophisticated parsing logic
        # For now, we are just getting the name and URL.
        # A more advanced version would search for phone numbers, addresses, etc.
        business_data['website'] = source_url
        business_data['phone'] = None # Placeholder
        business_data['address'] = None # Placeholder

        return business_data
