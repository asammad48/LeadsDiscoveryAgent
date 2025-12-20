from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError
from utils.http_client import http_client

@register_scraper
class GoogleSearchScraper(BaseScraper):
    platform = "google_search"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        search_url = f"https://www.google.com/search?q={query}"
        response = http_client.get(search_url)

        if not response:
            raise NoResultsFoundError(self.platform)

        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        # Parsing Local Pack (businesses with maps)
        for result in soup.select('.t_2_mdw.GgV1E'):
            name_el = result.select_one('.rllt__details .dbg0pd')
            phone_el = result.select_one('.rllt__details .Y2yqfc')
            address_el = result.select_one('.rllt__details .W4Efsd:last-child span:last-child')
            category_el = result.select_one('.rllt__details .W4Efsd:first-child span:first-child')

            if name_el:
                results.append({
                    'business_name': name_el.text,
                    'phone': phone_el.text if phone_el else None,
                    'address': address_el.text if address_el else None,
                    'category': category_el.text if category_el else None,
                    'platform': self.platform,
                    'source_url': "https://www.google.com" + result.select_one('a')['href'] if result.select_one('a') else None
                })

        # Fallback to organic results if Local Pack is not found
        if not results:
            for result in soup.select('.g'):
                name_el = result.select_one('h3')
                link_el = result.select_one('a')
                snippet_el = result.select_one('.IsZvec')

                if name_el and link_el:
                    results.append({
                        'business_name': name_el.text,
                        'description/snippet': snippet_el.text if snippet_el else None,
                        'platform': self.platform,
                        'source_url': link_el['href'] if link_el else None
                    })

        next_page_el = soup.select_one('a#pnnext')
        pagination_info = {'next_page_url': self._normalize_url(next_page_el['href'], base="https://www.google.com")} if next_page_el and 'href' in next_page_el.attrs else None

        return results, pagination_info

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        # Not used in this implementation
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        # Not used in this implementation
        return {}

    def _normalize_url(self, url: str, base: str = "") -> str:
        if url.startswith('/url?q='):
            return parse_qs(urlparse(url).query).get('q', [None])[0]
        if url.startswith('/'):
            return base + url
        return url
