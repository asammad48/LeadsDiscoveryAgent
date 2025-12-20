import pytest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from scrapers.google_search import GoogleSearchScraper
from scrapers.google_maps import GoogleMapsScraper
from scrapers.facebook import FacebookScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.instagram import InstagramScraper

DDGS_MOCK_RESULTS = [{'title': 'Test Business', 'body': 'Description', 'href': 'https://example.com'}]

@patch('ddgs.DDGS.text', return_value=DDGS_MOCK_RESULTS)
@patch('requests.get')
def test_google_search_scraper_live(mock_requests_get, mock_ddgs):
    mock_response = MagicMock()
    mock_response.content = b"<html><head><title>Test Business Page</title></head></html>"
    mock_requests_get.return_value = mock_response
    scraper = GoogleSearchScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business Page"

@patch('ddgs.DDGS.text', return_value=DDGS_MOCK_RESULTS)
@patch('requests.get')
def test_google_maps_scraper_live(mock_requests_get, mock_ddgs):
    mock_response = MagicMock()
    mock_response.content = b"<html><head><title>Test Business Maps - Google Maps</title></head></html>"
    mock_requests_get.return_value = mock_response
    scraper = GoogleMapsScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business Maps"

@patch('ddgs.DDGS.text', return_value=DDGS_MOCK_RESULTS)
def test_facebook_scraper_live(mock_ddgs):
    scraper = FacebookScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business"

@patch('ddgs.DDGS.text', return_value=DDGS_MOCK_RESULTS)
@patch('requests.get')
def test_linkedin_scraper_live(mock_requests_get, mock_ddgs):
    mock_response = MagicMock()
    mock_response.content = b"<html><head><title>Test Business | LinkedIn</title></head></html>"
    mock_requests_get.return_value = mock_response
    scraper = LinkedInScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business"

@patch('ddgs.DDGS.text', return_value=DDGS_MOCK_RESULTS)
@patch('requests.Session.get')
def test_instagram_scraper_live(mock_session_get, mock_ddgs):
    mock_response = MagicMock()
    mock_response.content = "<html><head><title>Test Business (@test) • Instagram photos and videos</title><meta name='description' content='Test description'></head></html>".encode('utf-8')
    mock_session_get.return_value = mock_response
    scraper = InstagramScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business (@test)"
    assert results[0]['description/snippet'] == "Test description"
