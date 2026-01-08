from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from ddgs import DDGS
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError
import asyncio

@register_scraper
class GoogleMapsScraper(BaseScraper):
    platform = "google_maps"

    async def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        print(f"Starting authoritative Google Maps scrape for query: {query}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}", wait_until='networkidle')

            # This is a crucial step: we need to scroll to load all results
            for _ in range(5): # Scroll a few times to load more results
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)

            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')

            results = []
            # Find all result containers
            place_links = soup.find_all('a', {'aria-label': True})

            for link in place_links:
                href = link.get('href')
                if href and '/maps/place/' in href:
                    try:
                        await page.goto(href, wait_until='networkidle')
                        place_html = await page.content()
                        place_soup = BeautifulSoup(place_html, 'html.parser')

                        business_data = self._parse_profile_page(place_soup, href)

                        if business_data.get("business_name"):
                            results.append(business_data)
                            print(f"  > Successfully extracted authoritative data for: {business_data['business_name']}")
                    except Exception as e:
                        print(f"  > An error occurred while processing {href}: {e}")

            await browser.close()

        if not results:
            raise NoResultsFoundError(self.platform)

        return results, None

    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        return []

    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        business_data = {
            'platform': self.platform,
            'source_url': source_url,
            'business_name': None,
            'website': None,
            'phone': None,
            'address': None,
        }

        name_tag = soup.find('h1')
        if name_tag:
            business_data['business_name'] = name_tag.get_text(strip=True)

        for tag in soup.find_all(['button', 'a'], attrs={'aria-label': True}):
            label = tag['aria-label']
            if label.lower().startswith('address:'):
                business_data['address'] = label.replace('Address:', '').strip()
            elif label.lower().startswith('website:'):
                business_data['website'] = tag.get('href')
            elif label.lower().startswith('phone:'):
                business_data['phone'] = label.replace('Phone:', '').strip()

        return business_data
