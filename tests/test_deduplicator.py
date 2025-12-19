import sys
import os
import unittest

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from modules.deduplicator import Deduplicator
from agent.models.lead import Lead

class TestDeduplicator(unittest.TestCase):
    """Unit tests for the Deduplicator class."""

    def setUp(self):
        """Set up a Deduplicator instance for each test."""
        self.deduplicator = Deduplicator()

    def test_deduplicate_by_website(self):
        """Test that leads with the same website are deduplicated and merged."""
        leads = [
            Lead(name="John Doe", company="Acme Inc.", city="SF", website="acme.com", source="Google"),
            Lead(name="Jane Smith", company="Acme Inc.", city="SF", website="acme.com", source="LinkedIn", email="jane@acme.com"),
        ]
        deduplicated_leads = self.deduplicator.deduplicate(leads)
        self.assertEqual(len(deduplicated_leads), 1)
        self.assertEqual(deduplicated_leads[0].source, "Google, LinkedIn")
        self.assertEqual(deduplicated_leads[0].email, "jane@acme.com")

    def test_deduplicate_by_company_city_fallback(self):
        """Test that leads with the same company and city are deduplicated when website is absent."""
        leads = [
            Lead(name="John Doe", company="Beta Corp.", city="NY", source="Facebook"),
            Lead(name="Jane Smith", company="Beta Corp.", city="NY", source="Instagram", phone="123-456-7890"),
        ]
        deduplicated_leads = self.deduplicator.deduplicate(leads)
        self.assertEqual(len(deduplicated_leads), 1)
        self.assertEqual(deduplicated_leads[0].source, "Facebook, Instagram")
        self.assertEqual(deduplicated_leads[0].phone, "123-456-7890")

    def test_deduplicate_by_company_different_city(self):
        """Test that leads with the same company but different city are not deduplicated."""
        leads = [
            Lead(name="John Doe", company="Beta Corp.", city="NY", source="Facebook"),
            Lead(name="Jane Smith", company="Beta Corp.", city="LA", source="Instagram"),
        ]
        deduplicated_leads = self.deduplicator.deduplicate(leads)
        self.assertEqual(len(deduplicated_leads), 2)

    def test_merge_strategy(self):
        """Test the merging of various fields."""
        lead1 = Lead(name="John Doe", company="Gamma LLC", city="CHI", website="gamma.com", source="Google", linkedin_profile="linkedin.com/johndoe")
        lead2 = Lead(name="J. Doe", company="Gamma LLC", city="CHI", website="gamma.com", source="LinkedIn", title="Engineer", linkedin_profile="linkedin.com/johndoe2")

        deduplicated_leads = self.deduplicator.deduplicate([lead1, lead2])
        self.assertEqual(len(deduplicated_leads), 1)
        merged_lead = deduplicated_leads[0]
        self.assertEqual(merged_lead.source, "Google, LinkedIn")
        self.assertEqual(merged_lead.linkedin_profile, "linkedin.com/johndoe, linkedin.com/johndoe2")
        self.assertEqual(merged_lead.title, "Engineer")
        self.assertEqual(merged_lead.name, "John Doe") # Original name is kept

    def test_no_duplicates(self):
        """Test that a list with no duplicates remains unchanged."""
        leads = [
            Lead(name="John Doe", company="Acme Inc.", city="SF", website="acme.com"),
            Lead(name="Jane Smith", company="Beta Corp.", city="NY", website="beta.com"),
        ]
        deduplicated_leads = self.deduplicator.deduplicate(leads)
        self.assertEqual(len(deduplicated_leads), 2)

    def test_empty_list(self):
        """Test that an empty list of leads results in an empty list."""
        leads = []
        deduplicated_leads = self.deduplicator.deduplicate(leads)
        self.assertEqual(len(deduplicated_leads), 0)

    def test_mixed_deduplication(self):
        """Test a mix of website and company/city name deduplication."""
        leads = [
            Lead(name="Alpha", company="A Corp", city="SF", website="a.com", source="1"),
            Lead(name="Beta", company="B Corp", city="NY", source="2"),
            Lead(name="Alpha Prime", company="A Corp", city="SF", website="a.com", source="3"),
            Lead(name="Beta Prime", company="B Corp", city="NY", source="4", phone="555-1234"),
            Lead(name="Gamma", company="C Corp", city="CHI", website="c.com"),
        ]
        deduplicated_leads = self.deduplicator.deduplicate(leads)
        self.assertEqual(len(deduplicated_leads), 3)

        # Verify the merged leads
        lead_a = next(l for l in deduplicated_leads if l.company == "A Corp")
        self.assertEqual(lead_a.source, "1, 3")

        lead_b = next(l for l in deduplicated_leads if l.company == "B Corp")
        self.assertEqual(lead_b.source, "2, 4")
        self.assertEqual(lead_b.phone, "555-1234")

    def test_transitive_deduplication(self):
        """Test that leads linked transitively are merged correctly."""
        leads = [
            # Lead A and B share a company/city
            Lead(name="Lead A", company="CorpX", city="CityY", source="Source1"),
            Lead(name="Lead B", company="CorpX", city="CityY", source="Source2"),
            # Lead C and D share a website
            Lead(name="Lead C", website="corpy.com", source="Source3", company="CorpY"),
            Lead(name="Lead D", website="corpy.com", source="Source4", company="CorpY"),
            # Lead E links B and C by sharing company/city with B and website with C
            Lead(name="Lead E", company="CorpX", city="CityY", website="corpy.com", source="Source5")
        ]

        deduplicated_leads = self.deduplicator.deduplicate(leads)

        self.assertEqual(len(deduplicated_leads), 1)
        merged_lead = deduplicated_leads[0]

        expected_sources = "Source1, Source2, Source3, Source4, Source5"
        self.assertEqual(merged_lead.source, expected_sources)


if __name__ == '__main__':
    unittest.main()
