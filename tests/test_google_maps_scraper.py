import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.sources.google_maps_scraper import GoogleMapsScraper
from src.agent.models.lead import Lead

class TestGoogleMapsScraper(unittest.TestCase):

    @patch('src.agent.sources.google_maps_scraper.webdriver.Chrome')
    def test_initialization(self, mock_chrome):
        scraper = GoogleMapsScraper(query="test")
        self.assertIsNotNone(scraper.driver)
        scraper.driver.quit()

    @patch('src.agent.sources.google_maps_scraper.webdriver.Chrome')
    def test_scrape_place_details(self, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        mock_name_element = MagicMock()
        mock_name_element.text = "Test Business"
        mock_address_element = MagicMock()
        mock_address_element.get_attribute.return_value = "Address: 123 Test St, Test City, TS 123"
        mock_website_element = MagicMock()
        mock_website_element.get_attribute.return_value = "Website: http://test.com"
        mock_phone_element = MagicMock()
        mock_phone_element.get_attribute.return_value = "Phone: 555-1234"
        mock_category_element = MagicMock()
        mock_category_element.text = "Restaurant"

        mock_elements = {
            (By.CSS_SELECTOR, "h1"): mock_name_element,
            (By.CSS_SELECTOR, "[aria-label*='Address:']"): mock_address_element,
            (By.CSS_SELECTOR, "[aria-label*='Website:']"): mock_website_element,
            (By.CSS_SELECTOR, "[aria-label*='Phone:']"): mock_phone_element,
            (By.XPATH, "//button[contains(@jsaction, 'category')]"): mock_category_element,
        }

        def find_element_side_effect(by, value):
            return mock_elements.get((by, value))

        mock_driver.find_element.side_effect = find_element_side_effect

        with GoogleMapsScraper(query="test") as scraper:
            scraper.driver = mock_driver
            result = scraper._scrape_place_details()

        self.assertEqual(result["name"], "Test Business")
        self.assertEqual(result["city"], "Test City")
        self.assertEqual(result["website"], "http://test.com")
        self.assertEqual(result["phone"], "555-1234")

    @patch('src.agent.sources.google_maps_scraper.webdriver.Chrome')
    @patch('src.agent.sources.google_maps_scraper.WebDriverWait')
    def test_scrape_returns_lead_objects(self, mock_wait, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        mock_feed_element = MagicMock()
        mock_link = MagicMock()
        mock_link.get_attribute.return_value = "http://fake-url.com/1"
        mock_feed_element.find_elements.return_value = [mock_link]
        mock_driver.find_element.return_value = mock_feed_element
        mock_driver.window_handles = ['main', 'new']
        mock_driver.current_window_handle = 'main'


        with GoogleMapsScraper(query="test") as scraper:
            scraper.driver = mock_driver
            # Mock the details scraping to return a dictionary
            scraper._scrape_place_details = MagicMock(return_value={
                "name": "Test Business", "company": "Test Business", "city": "Test City",
                "website": "http://test.com", "phone": "555-1234",
                "notes": "Category: Restaurant", "source": "Google Maps"
            })
            results = scraper.scrape()

        self.assertIsInstance(results[0], Lead)
        self.assertEqual(results[0].name, "Test Business")


if __name__ == '__main__':
    unittest.main()
