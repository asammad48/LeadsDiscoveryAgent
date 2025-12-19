import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from modules.google_maps_scraper import GoogleMapsScraper

class TestGoogleMapsScraper(unittest.TestCase):
    """
    A class to test the GoogleMapsScraper.
    """

    @patch('modules.google_maps_scraper.webdriver.Chrome')
    def test_initialization(self, mock_chrome):
        """
        Tests that the scraper can be initialized.
        """
        scraper = GoogleMapsScraper()
        self.assertIsNotNone(scraper.driver)

    @patch('modules.google_maps_scraper.WebDriverWait')
    @patch('modules.google_maps_scraper.webdriver.Chrome')
    def test_scrape_place_details(self, mock_chrome, mock_wait):
        """
        Tests the data extraction logic for a single place.
        """
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Mock the elements that will be found on the page
        mock_name_element = MagicMock()
        mock_name_element.text = "Test Business"

        mock_address_element = MagicMock()
        mock_address_element.get_attribute.return_value = "Address: 123 Test St"

        mock_website_element = MagicMock()
        mock_website_element.get_attribute.return_value = "Website: http://test.com"

        mock_phone_element = MagicMock()
        mock_phone_element.get_attribute.return_value = "Phone: 555-1234"

        mock_category_element = MagicMock()
        mock_category_element.text = "Restaurant"

        # Create a dictionary to map selectors to the mock elements
        mock_elements = {
            (By.CSS_SELECTOR, "h1"): mock_name_element,
            (By.CSS_SELECTOR, "[aria-label*='Address:']"): mock_address_element,
            (By.CSS_SELECTOR, "[aria-label*='Website:']"): mock_website_element,
            (By.CSS_SELECTOR, "[aria-label*='Phone:']"): mock_phone_element,
            (By.XPATH, "//button[contains(@jsaction, 'category')]"): mock_category_element,
        }

        # The side_effect function returns the correct mock element based on the selector
        def find_element_side_effect(by, value):
            return mock_elements.get((by, value))

        mock_driver.find_element.side_effect = find_element_side_effect

        scraper = GoogleMapsScraper()
        scraper.driver = mock_driver

        result = scraper._scrape_place_details()

        self.assertEqual(result["name"], "Test Business")
        self.assertEqual(result["address"], "123 Test St")
        self.assertEqual(result["website"], "http://test.com")
        self.assertEqual(result["phone"], "555-1234")
        self.assertEqual(result["category"], "Restaurant")

    @patch('modules.google_maps_scraper.time.sleep')
    @patch('modules.google_maps_scraper.WebDriverWait')
    @patch('modules.google_maps_scraper.webdriver.Chrome')
    def test_scrape_multiple_pages(self, mock_chrome, mock_wait, mock_sleep):
        """
        Tests the pagination logic for scraping multiple pages.
        """
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Mock the feed element and the links within it
        mock_feed_element = MagicMock()
        mock_feed_element.find_elements.side_effect = [
            [MagicMock(get_attribute=lambda x: "http://fake-url.com/1")],
            [MagicMock(get_attribute=lambda x: "http://fake-url.com/2")],
        ]
        mock_driver.find_element.return_value = mock_feed_element

        # Mock the "Next page" button to be clickable once, then raise a TimeoutException
        mock_next_button = MagicMock()
        mock_wait.return_value.until.side_effect = [
            True,               # For the search box
            True,               # For the initial search results
            True,               # For the new window handle on page 1
            mock_next_button,   # For the first "Next page" click
            True,               # For the URL change after the first click
            True,               # For the new window handle on page 2
        ]

        scraper = GoogleMapsScraper()
        scraper.driver = mock_driver
        scraper._scrape_place_details = MagicMock(return_value={"name": "Test"})

        results = scraper.scrape("test", num_pages=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(scraper._scrape_place_details.call_count, 2)
        mock_next_button.click.assert_called_once()


if __name__ == '__main__':
    unittest.main()
