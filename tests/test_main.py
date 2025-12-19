import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to python path to allow imports like 'from src.agent.main import run_query'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.main import run_query
from src.agent.models.lead import Lead

class TestMainOrchestrator(unittest.TestCase):

    @patch('src.agent.main.ExcelWriter')
    @patch('src.agent.main.Deduplicator')
    @patch('src.agent.main.Scorer')
    @patch('src.agent.main.discover_scrapers')
    @patch('src.agent.main.KeywordExpander')
    @patch('src.agent.main.IntentParser')
    def test_orchestrator_flow(self, MockIntentParser, MockKeywordExpander, mock_discover_scrapers, MockScorer, MockDeduplicator, MockExcelWriter):
        # 1. Setup Mocks
        mock_intent_parser = MockIntentParser.return_value
        mock_intent_parser.parse.return_value = {'industry': 'hotels', 'location': 'england'}

        mock_keyword_expander = MockKeywordExpander.return_value
        mock_keyword_expander.expand.return_value = {'expanded_keywords': ['hotels in england']}

        # Mock scraper classes returned by discover_scrapers
        MockScraperClass1 = MagicMock()
        MockScraperClass1.__name__ = "MockScraper1"
        MockScraperClass2 = MagicMock()
        MockScraperClass2.__name__ = "MockScraper2"
        mock_discover_scrapers.return_value = [MockScraperClass1, MockScraperClass2]

        mock_scorer = MockScorer.return_value
        mock_scorer.score.return_value = 85

        mock_deduplicator = MockDeduplicator.return_value
        deduplicated_list = [
            Lead(name='Lead 1', company='Company 1'),
            Lead(name='Lead 2', company='Company 2'),
            Lead(name='Lead 3', company='Company 3')
        ]
        mock_deduplicator.deduplicate.return_value = deduplicated_list

        mock_excel_writer = MockExcelWriter.return_value

        # 2. Call the function under test
        query = "Hotels in England that may need POS"
        run_query(query)

        # 3. Assertions
        MockIntentParser.assert_called_once()
        mock_intent_parser.parse.assert_called_with(query)

        MockKeywordExpander.assert_called_once()
        mock_keyword_expander.expand.assert_called_with({'industry': 'hotels', 'location': 'england'})

        mock_discover_scrapers.assert_called_once()

        MockScorer.assert_called_once()
        # Inside run_query, 2 mock scrapers are discovered, and each produces 2 mock leads. So 4 leads total.
        self.assertEqual(mock_scorer.score.call_count, 4)

        MockDeduplicator.assert_called_once()
        # The argument to deduplicate should be the list of 4 leads created inside run_query
        self.assertEqual(len(mock_deduplicator.deduplicate.call_args[0][0]), 4)

        MockExcelWriter.assert_called_once_with(filename="leads_output.xlsx")
        mock_excel_writer.save.assert_called_once_with(deduplicated_list)


if __name__ == '__main__':
    unittest.main()
