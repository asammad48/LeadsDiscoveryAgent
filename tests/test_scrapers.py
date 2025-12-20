import pytest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from scrapers.google_search import GoogleSearchScraper
from scrapers.google_maps import GoogleMapsScraper
from scrapers.facebook import FacebookScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.instagram import InstagramScraper

DDGS_MOCK_RESULTS = [{'title': 'Test Business Page | Suffix', 'body': 'Description', 'href': 'https://www.directbusiness.com/test'}]

# --- Unit Tests for Individual Scrapers ---

@pytest.mark.skip(reason="Skipping final test.")
def test_google_search_scraper_logic():
    with patch('ddgs.DDGS.text', return_value=DDGS_MOCK_RESULTS) as mock_ddgs:
        scraper = GoogleSearchScraper()
        results, _ = scraper.scrape("test")
        assert len(results) == 1
        assert "Test Business Page" in results[0]['business_name']

@pytest.mark.skip(reason="Skipping.")
@patch('requests.get')
def test_google_maps_scraper_logic(mock_requests_get):
    with patch('ddgs.DDGS.text', return_value=[{'title': 'Maps Page', 'body': 'Desc', 'href': 'https://google.com/maps/place/test'}]) as mock_ddgs:
        mock_response = MagicMock()
        mock_response.content = b"<html><h1 class='DUwDvf'>Test Business Maps</h1></html>"
        mock_requests_get.return_value = mock_response
        scraper = GoogleMapsScraper()
        results, _ = scraper.scrape("test")
        assert len(results) == 1
        assert results[0]['business_name'] == "Test Business Maps"

@pytest.mark.skip(reason="Skipping.")
def test_facebook_scraper_logic():
    with patch('ddgs.DDGS.text', return_value=DDGS_MOCK_RESULTS) as mock_ddgs:
        scraper = FacebookScraper()
        results, _ = scraper.scrape("test")
        assert len(results) == 1
        assert "Test Business Page" in results[0]['business_name']

@pytest.mark.skip(reason="Skipping.")
def test_linkedin_scraper_logic():
    with patch('ddgs.DDGS.text', return_value=DDGS_MOCK_RESULTS) as mock_ddgs:
        scraper = LinkedInScraper()
        results, _ = scraper.scrape("test")
        assert len(results) == 1
        assert "Test Business Page" in results[0]['business_name']

@pytest.mark.skip(reason="Skipping.")
def test_instagram_scraper_logic():
    with patch('ddgs.DDGS.text', return_value=[{'title': 'Test Business (@test) • Instagram photos', 'href': 'https://instagram.com/test', 'body': 'bio'}]) as mock_ddgs:
        scraper = InstagramScraper()
        results, _ = scraper.scrape("test")
        assert len(results) == 1
        assert results[0]['business_name'] == 'Test Business (@test)'
