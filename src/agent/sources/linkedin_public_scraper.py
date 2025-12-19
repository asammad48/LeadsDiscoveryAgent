import json
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from typing import List
import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agent.models.lead import Lead
from src.agent.sources.base_source import BaseSource

class LinkedInPublicScraper(BaseSource):
    """
    A scraper for fetching lead data from public LinkedIn company pages.
    """

    def __init__(self, query: str, max_results: int = 20):
        self.query = query
        self.max_results = max_results

    def scrape(self) -> List[Lead]:
        """
        Scrapes LinkedIn company pages for a given query.

        Returns:
            A list of Lead objects.
        """
        leads = []
        search_results = self._search_linkedin_google()

        for result in search_results:
            url = result['href']
            if self._is_company_url(url):
                company_data = self._scrape_linkedin_company_page(url)
                if company_data:
                    leads.append(Lead(
                        name=company_data.get('name'),
                        company=company_data.get('name'),
                        website=company_data.get('url'),
                        notes=company_data.get('description'),
                        source='LinkedIn',
                        linkedin_profile=url
                    ))
        return leads

    def _search_linkedin_google(self):
        """
        Searches Google for LinkedIn pages matching the query.
        """
        with DDGS() as ddgs:
            return list(ddgs.text(f"site:linkedin.com {self.query}", max_results=self.max_results))

    def _is_company_url(self, url: str) -> bool:
        """
        Checks if a URL is a LinkedIn company page URL.
        """
        return "/company/" in url and "/in/" not in url

    def _scrape_linkedin_company_page(self, url: str):
        """
        Scrapes a LinkedIn company page for public information.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        data = {}

        script_tag = soup.find('script', {'type': 'application/ld+json'})
        if script_tag:
            try:
                json_data = json.loads(script_tag.string)
                org_data = next((item for item in json_data.get('@graph', []) if item.get('@type') == 'Organization'), None)
                if org_data:
                    data['name'] = org_data.get('name')
                    data['description'] = org_data.get('description')
                    data['url'] = org_data.get('url')
            except (json.JSONDecodeError, KeyError, StopIteration):
                pass

        if not data.get('name'):
            name_tag = soup.find('h1', class_='top-card-layout__title')
            if name_tag:
                data['name'] = name_tag.get_text(strip=True)

        if not data.get('description'):
            description_section = soup.find('section', {'data-test-id': 'about-us__description'})
            if description_section:
                data['description'] = description_section.get_text(strip=True)

        return data
