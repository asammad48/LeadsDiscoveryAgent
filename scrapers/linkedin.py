from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError
from utils.http_client import http_client

@register_scraper
class LinkedInScraper(BaseScraper):
    platform = "linkedin"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        search_url = f"https://www.linkedin.com/public-guest/search/companies?keywords={query}"
        response = http_client.get(search_url)

        if not response:
            raise NoResultsFoundError(self.platform)

        soup = BeautifulSoup(response.text, 'html.parser')
        profile_urls = self._parse_search_results(soup)

        results = []
        for url in profile_urls:
            profile_response = http_client.get(url)
            if profile_response:
                profile_soup = BeautifulSoup(profile_response.text, 'html.parser')
                results.append(self._parse_profile_page(profile_soup, url))

        return results, None

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        urls = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'linkedin.com/company/' in href:
                urls.append(href)
        return list(set(urls))

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        business_name = None
        for selector in ['h1.top-card-layout__title', 'h1', '.org-top-card-summary__title', 'h1[slot="top-card-layout-entity-info__title"]']:
            element = soup.select_one(selector)
            if element:
                business_name = element.get_text(strip=True)
                break

        website = None
        for el in soup.select('a[rel="nofollow"]'):
            if "Visit website" in el.text:
                website = el['href']
                break
        if not website:
            website_el = soup.find('a', {'rel': 'nofollow', 'target': '_blank'})
            website = website_el['href'] if website_el else None

        description = soup.select_one('.about-section__description')

        return {
            'business_name': business_name or "N/A",
            'platform': self.platform,
            'website': website,
            'social_url': source_url,
            'source_url': source_url,
            'description/snippet': description.text.strip() if description else None
        }
