import os
import sys
import unittest
import pandas as pd

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from agent.models.lead import Lead
from agent.storage.excel_writer import ExcelWriter

class TestExcelWriter(unittest.TestCase):
    """Tests for the ExcelWriter class."""

    def setUp(self):
        """Set up for the tests."""
        self.filename = "test_leads.xlsx"
        self.writer = ExcelWriter(self.filename)
        # Ensure the file does not exist before each test
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def tearDown(self):
        """Tear down after the tests."""
        # Clean up the created file
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_save_new_leads(self):
        """Test saving leads to a new file."""
        leads = [
            Lead(name="John Doe", company="Test Corp", city="New York", website="http://test.com"),
            Lead(name="Jane Doe", company="Sample Inc", city="London", website="http://sample.com")
        ]
        self.writer.save(leads)

        df = pd.read_excel(self.filename)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['name'], "John Doe")
        self.assertEqual(df.iloc[1]['company'], "Sample Inc")

    def test_append_leads(self):
        """Test appending new leads to an existing file."""
        leads1 = [Lead(name="John Doe", company="Test Corp", city="New York", website="http://test.com")]
        self.writer.save(leads1)

        leads2 = [Lead(name="Jane Doe", company="Sample Inc", city="London", website="http://sample.com")]
        self.writer.save(leads2)

        df = pd.read_excel(self.filename)
        self.assertEqual(len(df), 2)

    def test_avoid_duplicates_by_website(self):
        """Test that duplicate leads (by website) are not added."""
        leads = [
            Lead(name="John Doe", company="Test Corp", city="New York", website="http://test.com"),
            Lead(name="John Doe Updated", company="Test Corp", city="New York", website="http://test.com")
        ]
        self.writer.save(leads)

        df = pd.read_excel(self.filename)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['name'], "John Doe Updated")

    def test_avoid_duplicates_by_company_city(self):
        """Test that duplicate leads (by company and city) are not added."""
        leads = [
            Lead(name="John Doe", company="Test Corp", city="New York", website=None),
            Lead(name="John Doe Updated", company="Test Corp", city="New York", website=None)
        ]
        self.writer.save(leads)

        df = pd.read_excel(self.filename)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['name'], "John Doe Updated")

    def test_save_no_leads(self):
        """Test that saving an empty list of leads does not create a file."""
        self.writer.save([])
        self.assertFalse(os.path.exists(self.filename))

    def test_mixed_duplicates(self):
        """Test a mix of new and duplicate leads."""
        leads1 = [
            Lead(name="John Doe", company="Test Corp", city="New York", website="http://test.com"),
            Lead(name="Jane Doe", company="Sample Inc", city="London", website=None)
        ]
        self.writer.save(leads1)

        leads2 = [
            Lead(name="John Doe Updated", company="Test Corp", city="New York", website="http://test.com"),
            Lead(name="New Guy", company="NewCo", city="Paris", website="http://new.co"),
            Lead(name="Jane Doe Updated", company="Sample Inc", city="London", website=None)
        ]
        self.writer.save(leads2)

        df = pd.read_excel(self.filename)
        self.assertEqual(len(df), 3)
        # Check that the updated records are present
        self.assertIn("John Doe Updated", df['name'].values)
        self.assertIn("Jane Doe Updated", df['name'].values)
        self.assertIn("New Guy", df['name'].values)

if __name__ == '__main__':
    unittest.main()
