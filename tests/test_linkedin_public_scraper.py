import sys
import os
import unittest
from unittest.mock import patch

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from modules.linkedin_public_scraper import is_company_url, is_profile_url

class TestLinkedInPublicScraper(unittest.TestCase):

    def test_is_company_url(self):
        self.assertTrue(is_company_url("https://www.linkedin.com/company/google"))
        self.assertFalse(is_company_url("https://www.linkedin.com/in/williamhgates"))
        self.assertFalse(is_company_url("https://www.linkedin.com/feed/"))

    def test_is_profile_url(self):
        self.assertTrue(is_profile_url("https://www.linkedin.com/in/williamhgates"))
        self.assertFalse(is_profile_url("https://www.linkedin.com/company/google"))
        self.assertFalse(is_profile_url("https://www.linkedin.com/feed/"))

if __name__ == '__main__':
    unittest.main()
