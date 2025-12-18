import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.intent_parser import IntentParser

class TestIntentParser(unittest.TestCase):

    def setUp(self):
        self.parser = IntentParser()

    def test_basic_query(self):
        query = "Hotels in England that may need POS"
        expected = {
            'industry': 'hotels',
            'location': 'england',
            'business_type': 'hotels',
            'pain_point_need': 'pos',
            'base_keywords': ['hotels', 'england']
        }
        self.assertEqual(self.parser.parse(query), expected)

    def test_complex_query(self):
        query = "Restaurants in London looking for a new website"
        expected = {
            'industry': 'restaurants',
            'location': 'london',
            'business_type': 'restaurants',
            'pain_point_need': 'website',
            'base_keywords': ['restaurants', 'london']
        }
        self.assertEqual(self.parser.parse(query), expected)

    def test_no_location(self):
        query = "Software companies that need marketing"
        expected = {
            'industry': 'software',
            'location': None,
            'business_type': 'software',
            'pain_point_need': 'marketing',
            'base_keywords': ['software']
        }
        actual = self.parser.parse(query)
        # Location might not be in keywords if None
        if actual.get('location'):
            expected['base_keywords'].append(actual['location'])
        self.assertEqual(actual, expected)


    def test_no_pain_point(self):
        query = "Clinics in New York"
        expected = {
            'industry': 'clinics',
            'location': 'new york',
            'business_type': 'clinics',
            'pain_point_need': None,
            'base_keywords': ['clinics', 'new york']
        }
        self.assertEqual(self.parser.parse(query), expected)

    def test_empty_query(self):
        query = ""
        expected = {
            'industry': None,
            'location': None,
            'business_type': None,
            'pain_point_need': None,
            'base_keywords': []
        }
        self.assertEqual(self.parser.parse(query), expected)

if __name__ == '__main__':
    unittest.main()
