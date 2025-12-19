import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.sources.linkedin_public_scraper import LinkedInPublicScraper
from src.agent.models.lead import Lead

class TestLinkedInPublicScraper(unittest.TestCase):

    @patch('src.agent.sources.linkedin_public_scraper.DDGS')
    @patch('src.agent.sources.linkedin_public_scraper.requests.get')
    def test_scrape_returns_leads(self, mock_get, mock_ddgs):
        # Mock DDGS search results
        mock_ddgs.return_value.__enter__.return_value.text.return_value = iter([
            {'href': 'https://www.linkedin.com/company/google'},
            {'href': 'https://www.linkedin.com/in/test-user'} # a profile, should be ignored
        ])

        # Mock requests.get for the company page
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><body>
            <script type="application/ld+json">
            {
                "@graph": [
                    {
                        "@type": "Organization",
                        "name": "Google",
                        "description": "A multinational technology company.",
                        "url": "https://google.com"
                    }
                ]
            }
            </script>
        </body></html>
        """
        mock_get.return_value = mock_response

        scraper = LinkedInPublicScraper(query="test query")
        leads = scraper.scrape()

        self.assertEqual(len(leads), 1)
        self.assertIsInstance(leads[0], Lead)
        self.assertEqual(leads[0].name, "Google")
        self.assertEqual(leads[0].website, "https://google.com")
        self.assertEqual(leads[0].source, "LinkedIn")

    def test_is_company_url(self):
        scraper = LinkedInPublicScraper(query="")
        self.assertTrue(scraper._is_company_url("https://www.linkedin.com/company/google"))
        self.assertFalse(scraper._is_company_url("https://www.linkedin.com/in/williamhgates"))

if __name__ == '__main__':
    unittest.main()
