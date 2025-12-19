import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the src directory to the Python path
# This is necessary for the test to find the modules in the src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from modules.google_scraper import scrape_google

class TestGoogleScraper(unittest.TestCase):

    @patch('modules.google_scraper.requests.get')
    def test_scrape_google_parses_html_correctly(self, mock_get):
        """
        Tests that the scrape_google function correctly parses a sample HTML string.
        """
        # Sample HTML content mimicking Google's search result structure
        sample_html = """
        <html>
            <body>
                <div class="g">
                    <div class="yuRUbf">
                        <a href="https://example.com/result1"><h3>Result 1 Title</h3></a>
                    </div>
                    <div class="VwiC3b">Result 1 Snippet</div>
                </div>
                <div class="g">
                    <div class="yuRUbf">
                        <a href="https://example.com/result2"><h3>Result 2 Title</h3></a>
                    </div>
                    <div class="VwiC3b">Result 2 Snippet</div>
                </div>
            </body>
        </html>
        """

        # Configure the mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        # Call the function
        results = scrape_google("test query")

        # Expected results
        expected_results = [
            {'title': 'Result 1 Title', 'url': 'https://example.com/result1', 'snippet': 'Result 1 Snippet'},
            {'title': 'Result 2 Title', 'url': 'https://example.com/result2', 'snippet': 'Result 2 Snippet'}
        ]

        self.assertEqual(results, expected_results)

if __name__ == '__main__':
    unittest.main()
