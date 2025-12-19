import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.sources.instagram_scraper import InstagramScraper
from src.agent.models.lead import Lead

class TestInstagramScraper(unittest.TestCase):
    """Unit tests for the InstagramScraper."""

    @patch('instaloader.Instaloader')
    def test_scrape_single_profile(self, MockInstaloader):
        # 1. Setup Mocks
        mock_loader_instance = MockInstaloader.return_value

        # Mock Profile object
        mock_profile = MagicMock()
        mock_profile.username = 'testuser'
        mock_profile.full_name = 'Test User'
        mock_profile.biography = 'This is a test bio. Contact me at test@example.com. Visit my site!'
        mock_profile.external_url = 'https://example.com'
        mock_profile.business_category_name = 'Software Company'

        # Configure the mock loader to return the mock profile
        mock_loader_instance.context = None # Mock the context attribute
        with patch('instaloader.Profile.from_username', return_value=mock_profile):

            # 2. Initialize the scraper
            scraper = InstagramScraper(usernames=['testuser'])

            # 3. Run the scrape method
            leads = scraper.scrape()

            # 4. Assert the results
            self.assertEqual(len(leads), 1)
            lead = leads[0]
            self.assertIsInstance(lead, Lead)
            self.assertEqual(lead.name, 'Test User')
            self.assertEqual(lead.company, 'Test User')
            self.assertEqual(lead.email, 'test@example.com')
            self.assertEqual(lead.website, 'https://example.com')
            self.assertEqual(lead.source, 'Instagram')
            self.assertIn('Bio: This is a test bio.', lead.notes)
            self.assertIn('Business Category: Software Company', lead.notes)

    @patch('instaloader.Instaloader')
    def test_hashtag_discovery(self, MockInstaloader):
        # 1. Setup Mocks
        mock_loader_instance = MockInstaloader.return_value
        mock_loader_instance.context = None

        # Mock Post and Profile objects
        mock_post = MagicMock()
        mock_post.owner_username = 'discovered_user'

        mock_hashtag = MagicMock()
        mock_hashtag.get_posts.return_value = [mock_post]

        mock_profile = MagicMock()
        mock_profile.username = 'discovered_user'
        mock_profile.full_name = 'Discovered User'
        mock_profile.biography = 'Bio with contact: discovered@email.com'
        mock_profile.external_url = None
        mock_profile.business_category_name = 'Artist'

        with patch('instaloader.Hashtag.from_name', return_value=mock_hashtag), \
             patch('instaloader.Profile.from_username', return_value=mock_profile):

            # 2. Initialize scraper with a hashtag
            scraper = InstagramScraper(hashtags=['test'], max_profiles_per_hashtag=1)

            # 3. Run scrape
            leads = scraper.scrape()

            # 4. Assert results
            self.assertEqual(len(leads), 1)
            lead = leads[0]
            self.assertEqual(lead.name, 'Discovered User')
            self.assertEqual(lead.email, 'discovered@email.com')

if __name__ == '__main__':
    unittest.main()
