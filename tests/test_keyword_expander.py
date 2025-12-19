import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from modules.keyword_expander import KeywordExpander

class TestKeywordExpander(unittest.TestCase):
    def setUp(self):
        """Set up a KeywordExpander instance before each test."""
        self.expander = KeywordExpander()

    def test_expand_hotels_pos_intent(self):
        """
        Tests the expansion of a typical intent for hotels needing POS systems.
        """
        intent = {
            "industry": "hotels",
            "location": "england",
            "pain_point_need": "pos",
        }

        result = self.expander.expand(intent)

        # Test top-level structure
        self.assertIn("expanded_keywords", result)
        self.assertIn("synonyms", result)
        self.assertIn("hashtags", result)
        self.assertIn("platform_specific", result)

        # Test expanded_keywords
        self.assertIsInstance(result["expanded_keywords"], list)
        self.assertTrue(any("hospitality point of sale" in s for s in result["expanded_keywords"]))
        self.assertTrue(any("hotels pos in england" in s for s in result["expanded_keywords"]))

        # Test hashtags
        self.assertIn("#hotels", result["hashtags"])
        self.assertIn("#pos", result["hashtags"])
        self.assertIn("#england", result["hashtags"])
        self.assertIn("#hospitality", result["hashtags"])

        # Test platform_specific structure
        self.assertIn("linkedin", result["platform_specific"])
        self.assertIn("google", result["platform_specific"])
        self.assertIn("facebook", result["platform_specific"])
        self.assertIn("instagram", result["platform_specific"])

        # Test a specific platform query
        linkedin_queries = result["platform_specific"]["linkedin"]
        self.assertIsInstance(linkedin_queries, list)
        # Check for the owner title and the location
        owner_query = next((q for q in linkedin_queries if 'title:"owner"' in q), None)
        self.assertIsNotNone(owner_query)
        self.assertIn('"england"', owner_query)
        # Check that all synonyms are present
        self.assertIn('"hotels" OR "hospitality" OR "lodging" OR "resorts" OR "inns"', owner_query)
        self.assertIn('"pos" OR "point of sale" OR "payment processing" OR "merchant services" OR "cash register system"', owner_query)

    def test_expand_with_missing_location(self):
        """
        Tests that expansion works correctly when location is not provided.
        """
        intent = {
            "industry": "clinics",
            "pain_point_need": "website",
        }
        result = self.expander.expand(intent)

        self.assertIn("#clinics", result["hashtags"])
        self.assertNotIn("#None", "".join(result["hashtags"]))

        google_queries = result["platform_specific"]["google"]
        # Ensure no query fails due to a missing location
        self.assertFalse(any('inurl:"contact" site:*.None' in q for q in google_queries))


if __name__ == '__main__':
    unittest.main()
