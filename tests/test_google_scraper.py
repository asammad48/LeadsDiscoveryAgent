import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.sources.google_scraper import GoogleScraper
from src.agent.models.lead import Lead

class TestGoogleScraper(unittest.TestCase):

    @patch('src.agent.sources.google_scraper.requests.get')
    def test_scrape_google_parses_html_correctly(self, mock_get):
        """
        Tests that the GoogleScraper class correctly parses a sample HTML string.
        """
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

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        scraper = GoogleScraper(query="test query")
        results = scraper.scrape()

        expected_leads = [
            Lead(name='Result 1 Title', company='Result 1 Title', website='https://example.com/result1', notes='Result 1 Snippet', source='Google'),
            Lead(name='Result 2 Title', company='Result 2 Title', website='https://example.com/result2', notes='Result 2 Snippet', source='Google')
        ]

        self.assertEqual(len(results), len(expected_leads))
        for i, lead in enumerate(results):
            self.assertEqual(lead.name, expected_leads[i].name)
            self.assertEqual(lead.website, expected_leads[i].website)
            self.assertEqual(lead.notes, expected_leads[i].notes)

if __name__ == '__main__':
    unittest.main()
