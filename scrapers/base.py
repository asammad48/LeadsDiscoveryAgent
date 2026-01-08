from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import asyncio

class BaseScraper(ABC):
    platform: str

    @abstractmethod
    async def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        """
        The main asynchronous entry point for the scraper.
        """
        pass

    @abstractmethod
    def _parse_search_results(self, soup: BeautifulSoup) -> list[str]:
        """
        Parses a search results page to extract URLs to individual profile pages.
        """
        pass

    @abstractmethod
    def _parse_profile_page(self, soup: BeautifulSoup, source_url: str) -> dict:
        """
        Parses an individual profile page to extract the required business data.
        """
        pass
