import pytest
from unittest.mock import MagicMock, patch
from scrapers.google_search import GoogleSearchScraper
from scrapers.google_maps import GoogleMapsScraper
from scrapers.facebook import FacebookScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.instagram import InstagramScraper
import utils.http_client

# Mock data for DDGS
DDGS_MOCK_RESULTS = [{'title': 'Test Business', 'body': 'Description', 'href': 'https://example.com'}]

# Google Search
def test_google_search_scraper_live(mocker):
    mocker.patch('duckduckgo_search.DDGS.text', return_value=DDGS_MOCK_RESULTS)
    scraper = GoogleSearchScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business"

# Google Maps
def test_google_maps_scraper_live(mocker):
    mocker.patch('duckduckgo_search.DDGS.text', return_value=[{'title': 'Test Business Maps', 'body': 'Description', 'href': 'https://example.com'}])
    scraper = GoogleMapsScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business Maps"

# Facebook
@patch('scrapers.facebook.get_posts', return_value=[{'username': 'Test Business Facebook', 'text': 'Description', 'post_url': 'https://example.com'}])
def test_facebook_scraper_live(mock_get_posts):
    scraper = FacebookScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business Facebook"

# LinkedIn
def test_linkedin_scraper_live(mocker):
    mocker.patch('duckduckgo_search.DDGS.text', return_value=DDGS_MOCK_RESULTS)
    scraper = LinkedInScraper()
    results, _ = scraper.scrape("test")
    assert "Test Business" in results[0]['business_name']

# Instagram
def test_instagram_scraper_live(mocker):
    mocker.patch('duckduckgo_search.DDGS.text', return_value=[{'title': 'Test Business Instagram', 'body': 'Description', 'href': 'https://example.com'}])
    scraper = InstagramScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business Instagram"
