import pytest
import os
from bs4 import BeautifulSoup
from scrapers.google_maps import GoogleMapsScraper
from scrapers.linkedin import LinkedInScraper
from scrapers.instagram import InstagramScraper

def read_sample(samples_dir, filename):
    # This helper function might not be used if tests are self-contained
    try:
        with open(os.path.join(samples_dir, filename), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# Google Maps Tests
def test_google_maps_scraper_parse_profile_page():
    html = "<html><head><title>Test Business from Google Maps - Google Maps</title></head><body>+1 555-123-4567</body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    scraper = GoogleMapsScraper()
    result = scraper._parse_profile_page(soup, "https://example.com")
    assert result['business_name'] == "Test Business from Google Maps"
    assert result['phone'] == "+1 555-123-4567"

# LinkedIn Tests
def test_linkedin_scraper_parse_profile_page():
    html = "<html><head><title>Test Business | LinkedIn</title></head></html>"
    soup = BeautifulSoup(html, 'html.parser')
    scraper = LinkedInScraper()
    result = scraper._parse_profile_page(soup, "https://linkedin.com/company/test")
    assert result['business_name'] == "Test Business"

# Instagram Tests
def test_instagram_scraper_parse_profile_page():
    html = "<html><head><title>Test Business (@test) • Instagram photos and videos</title><meta name='description' content='Test description'></head></html>"
    soup = BeautifulSoup(html, 'html.parser')
    scraper = InstagramScraper()
    result = scraper._parse_profile_page(soup, "https://instagram.com/test")
    assert result['business_name'] == "Test Business (@test)"
    assert result['description/snippet'] == "Test description"
