import unittest
import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from modules.scorer import Scorer
from agent.models.lead import Lead

class TestScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = Scorer()
        self.sample_lead = Lead(
            name="The Grand Hotel",
            company="The Grand Hotel",
            title="General Manager",
            notes="A grand hotel in london, looking for a new POS system.",
            website="www.grandhotel.com",
            source="linkedin"
        )
        self.sample_intent = {
            "industry": "hotel",
            "location": "london",
            "pain_point_need": "pos"
        }
        self.sample_expanded_keywords = {
            "expanded_keywords": [
                "hotel pos",
                "hotel point of sale",
                "hotel in london",
                "grand hotel"
            ]
        }

    def test_score_calculation(self):
        score = self.scorer.score(self.sample_lead, self.sample_expanded_keywords, self.sample_intent)

        # Expected Score Calculation:
        # Keyword Score: 2/4 keywords match = 50. 50 * 0.4 = 20
        # Location Score: "london" is in notes = 100. 100 * 0.2 = 20
        # Industry Score: "hotel" is in notes = 100. 100 * 0.2 = 20
        # Contact Info Score: has website = 100. 100 * 0.1 = 10
        # Platform Reliability: "linkedin" = 90. 90 * 0.1 = 9
        # Total Score: 20 + 20 + 20 + 10 + 9 = 79
        self.assertEqual(score, 79)

    def test_filter_leads(self):
        leads = [
            self.sample_lead,
            Lead(name="No Match Cafe", company="No Match Cafe", source="google"), # Low score
            Lead(name="Another Hotel", company="Another Hotel", notes="A hotel in paris", source="facebook") # Medium score
        ]

        filtered_leads = self.scorer.filter_leads(leads, self.sample_expanded_keywords, self.sample_intent, 70)

        self.assertEqual(len(filtered_leads), 1)
        self.assertEqual(filtered_leads[0].name, "The Grand Hotel")

if __name__ == '__main__':
    unittest.main()
