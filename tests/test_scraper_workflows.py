import pytest
from unittest.mock import MagicMock, patch
from scrapers.google_search import GoogleSearchScraper
from scrapers.google_maps import GoogleMapsScraper
from scrapers.facebook import FacebookScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.instagram import InstagramScraper
from scrapers.directory import DirectoryScraper
import utils.http_client

# Google Search
def test_google_search_scraper_live(mocker):
    mocker.patch('utils.http_client.http_client.get', return_value=MagicMock(text='<div class="t_2_mdw GgV1E"><div class="rllt__details"><div class="dbg0pd">Test Business 1</div></div></div>'))
    scraper = GoogleSearchScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business 1"

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
    mocker.patch('utils.http_client.http_client.get', side_effect=[
        MagicMock(text='<a href="https://linkedin.com/company/test"></a>'),
        MagicMock(text='<h1>Test Business LinkedIn</h1>')
    ])
    scraper = LinkedInScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business LinkedIn"

# Instagram
def test_instagram_scraper_live(mocker):
    mocker.patch('duckduckgo_search.DDGS.text', return_value=[{'title': 'Test Business Instagram', 'body': 'Description', 'href': 'https://example.com'}])
    scraper = InstagramScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business Instagram"

# Directory
def test_directory_scraper_live(mocker):
    mocker.patch('utils.http_client.http_client.get', side_effect=[
        MagicMock(text='<div class="result"><a class="business-name" href="/biz/test"><span>Test Business Directory</span></a></div>'),
    ])
    scraper = DirectoryScraper()
    results, _ = scraper.scrape("test")
    assert results[0]['business_name'] == "Test Business Directory"
