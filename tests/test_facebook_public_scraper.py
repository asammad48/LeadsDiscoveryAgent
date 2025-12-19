import unittest
from unittest.mock import patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.agent.sources.facebook_public_scraper import FacebookPublicScraper
from src.agent.models.lead import Lead

class TestFacebookPublicScraper(unittest.TestCase):
    """Unit tests for the FacebookPublicScraper."""

    @patch('src.agent.sources.facebook_public_scraper.get_profile')
    @patch('src.agent.sources.facebook_public_scraper.get_posts')
    def test_scrape_page(self, mock_get_posts, mock_get_profile):
        mock_get_profile.return_value = {'Name': 'Test Page', 'Website': 'https://page.com'}
        mock_get_posts.return_value = [{'text': 'Contact at page@example.com'}]
        scraper = FacebookPublicScraper(target_id='test_page', target_type='page')
        leads = scraper.scrape()
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0].name, 'Test Page')
        self.assertEqual(leads[0].email, 'page@example.com')

    @patch('src.agent.sources.facebook_public_scraper.get_group_info')
    @patch('src.agent.sources.facebook_public_scraper.get_posts')
    def test_scrape_group(self, mock_get_posts, mock_get_group_info):
        mock_get_group_info.return_value = {'name': 'Test Group', 'members': 100}
        mock_get_posts.return_value = [{'text': 'Contact at group@example.com'}]
        scraper = FacebookPublicScraper(target_id='test_group', target_type='group')
        leads = scraper.scrape()
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0].name, 'Test Group')
        self.assertEqual(leads[0].email, 'group@example.com')

    @patch('src.agent.sources.facebook_public_scraper.get_profile')
    @patch('src.agent.sources.facebook_public_scraper.get_posts')
    def test_keyword_filtering(self, mock_get_posts, mock_get_profile):
        mock_get_profile.return_value = {'Name': 'Test Page'}
        mock_get_posts.return_value = [
            {'text': 'We have a special offer! offer@example.com'},
            {'text': 'Just a regular post. regular@example.com'}
        ]
        scraper = FacebookPublicScraper(target_id='test_page', keywords=['offer'])
        leads = scraper.scrape()
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0].email, 'offer@example.com')

if __name__ == '__main__':
    unittest.main()
