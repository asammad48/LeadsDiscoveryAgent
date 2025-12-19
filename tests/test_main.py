import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import os

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.main import generate_leads
from src.agent.models.lead import Lead

class TestMainOrchestrator(unittest.TestCase):

    @patch('src.agent.main.Deduplicator')
    @patch('src.agent.main.Scorer')
    @patch('src.agent.main.discover_scrapers')
    @patch('src.agent.main.KeywordExpander')
    @patch('src.agent.main.IntentParser')
    def test_orchestrator_flow(self, MockIntentParser, MockKeywordExpander, mock_discover_scrapers, MockScorer, MockDeduplicator):
        # 1. Setup Mocks
        mock_intent_parser = MockIntentParser.return_value
        mock_intent_parser.parse.return_value = {'industry': 'hotels', 'location': 'england'}

        mock_keyword_expander = MockKeywordExpander.return_value
        mock_keyword_expander.expand.return_value = {
            'expanded_keywords': ['hotels in england'],
            'platform_specific': {'google': ['google query'], 'linkedin': ['linkedin query']}
        }

        # Mock scraper classes and their instances
        mock_google_scraper_instance = Mock()
        mock_google_scraper_instance.scrape.return_value = [Lead(name='Google Lead', company='Google')]

        mock_linkedin_scraper_instance = Mock()
        mock_linkedin_scraper_instance.scrape.return_value = [Lead(name='LinkedIn Lead', company='LinkedIn')]

        MockGoogleScraper = MagicMock(return_value=mock_google_scraper_instance)
        MockGoogleScraper.__name__ = "GoogleScraper"

        MockLinkedInScraper = MagicMock(return_value=mock_linkedin_scraper_instance)
        MockLinkedInScraper.__name__ = "LinkedInPublicScraper"

        mock_discover_scrapers.return_value = [MockGoogleScraper, MockLinkedInScraper]

        mock_scorer = MockScorer.return_value
        mock_scorer.score.return_value = 85

        mock_deduplicator = MockDeduplicator.return_value
        deduplicated_list = [Lead(name='Lead 1', company='Company 1'), Lead(name='Lead 2', company='Company 2')]
        mock_deduplicator.deduplicate.return_value = deduplicated_list

        # 2. Call the function under test
        query = "Hotels in England that may need POS"
        result = generate_leads(query, selected_scraper_names=["GoogleScraper", "LinkedInPublicScraper"])

        # 3. Assertions
        MockIntentParser.assert_called_once()
        mock_intent_parser.parse.assert_called_with(query)

        MockKeywordExpander.assert_called_once()
        mock_keyword_expander.expand.assert_called_with({'industry': 'hotels', 'location': 'england'})

        mock_discover_scrapers.assert_called_once()

        # Assert that scraper classes are instantiated with the correct queries
        MockGoogleScraper.assert_called_with(query='google query')
        MockLinkedInScraper.assert_called_with(query='linkedin query')

        # Assert that the scrape method was called on each instance
        mock_google_scraper_instance.scrape.assert_called_once()
        mock_linkedin_scraper_instance.scrape.assert_called_once()

        MockScorer.assert_called_once()
        self.assertEqual(mock_scorer.score.call_count, 2)

        MockDeduplicator.assert_called_once()
        self.assertEqual(len(mock_deduplicator.deduplicate.call_args[0][0]), 2)

        # Check the final returned leads
        self.assertEqual(result['leads'], deduplicated_list)
        self.assertEqual(result['total_scraped'], 2)


if __name__ == '__main__':
    unittest.main()
