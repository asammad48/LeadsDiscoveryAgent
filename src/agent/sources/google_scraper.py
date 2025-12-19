import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Any
import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agent.models.lead import Lead
from src.agent.sources.base_source import BaseSource

class GoogleScraper(BaseSource):
    """
    A scraper for fetching lead data from Google search results.
    """

    def __init__(self, query: str, num_pages: int = 1):
        self.query = query
        self.num_pages = num_pages

    def scrape(self) -> List[Lead]:
        """
        Scrapes Google search results for a given query.

        Returns:
            A list of Lead objects.
        """
        results = []
        for page in range(self.num_pages):
            start = page * 10
            url = f"https://www.google.com/search?q={self.query}&start={start}"

            # Rotate user agents to avoid being blocked
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
            ]
            headers = {'User-Agent': random.choice(user_agents)}

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an exception for bad status codes

                soup = BeautifulSoup(response.text, 'html.parser')

                for g in soup.find_all('div', class_='g'):
                    rc = g.find('div', class_='yuRUbf')
                    if rc:
                        link_tag = rc.find('a')
                        title_tag = rc.find('h3')

                        if link_tag and title_tag:
                            url = link_tag['href']
                            title = title_tag.get_text()

                            snippet_tag = g.find('div', class_='VwiC3b')
                            snippet = snippet_tag.get_text() if snippet_tag else ""

                            lead = Lead(
                                name=title,
                                company=title, # Placeholder, can be improved with more advanced parsing
                                website=url,
                                notes=snippet,
                                source='Google'
                            )
                            results.append(lead)

                time.sleep(random.uniform(1, 3))

            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                break

        return results
