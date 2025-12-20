from bs4 import BeautifulSoup
from urllib.parse import urljoin
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError
from utils.http_client import http_client

@register_scraper
class DirectoryScraper(BaseScraper):
    platform = "directory"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        search_url = f"https://www.yellowpages.com/search?search_terms={query}"
        response = http_client.get(search_url)

        if not response:
            raise NoResultsFoundError(self.platform)

        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for result in soup.select('.result'):
            data = self._parse_profile_page(result, "https://www.yellowpages.com")
            results.append(data)

        next_page_el = soup.select_one('a.next')
        pagination_info = {'next_page_url': urljoin("https://www.yellowpages.com", next_page_el['href'])} if next_page_el and 'href' in next_page_el.attrs else None

        return results, pagination_info

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        # Unit testing only
        urls = []
        for link in soup.select('a.business-name'):
            href = link.get('href')
            if href:
                urls.append(urljoin("https://www.yellowpages.com", href))
        return list(set(urls))

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        business_name_el = soup.select_one('a.business-name span')
        if not business_name_el:
            business_name_el = soup.find('h1', class_='business-name')

        phone_el = soup.select_one('div.phones.phone.primary')
        if not phone_el:
            phone_el = soup.find('p', class_='phone')

        website_el = soup.select_one('a.track-visit-website')
        if not website_el:
            website_el = soup.select_one('a.website-link')

        return {
            'business_name': business_name_el.text.strip() if business_name_el else "N/A",
            'platform': self.platform,
            'phone': phone_el.text.strip() if phone_el else None,
            'website': website_el['href'] if website_el else None,
            'source_url': urljoin(source_url, soup.select_one('a.business-name')['href']) if soup.select_one('a.business-name') else None
        }
