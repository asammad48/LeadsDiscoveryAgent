import unittest
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.web_search import search_web
from src.modules.excel_storage import ExcelStorage

class TestModules(unittest.TestCase):

    def test_search_web(self):
        """
        Test that the web search returns a list of strings.
        """
        results = search_web("test query")
        self.assertIsInstance(results, list)
        if results:
            self.assertIsInstance(results[0], str)

    def test_excel_storage(self):
        """
        Test that the Excel storage creates a file.
        """
        storage = ExcelStorage()
        test_data = [{"test": "data"}]
        filename = "unittest_test.xlsx"
        storage.save_to_excel(test_data, filename)

        filepath = os.path.join(storage.data_dir, filename)
        self.assertTrue(os.path.exists(filepath))
        os.remove(filepath)

if __name__ == '__main__':
    unittest.main()
