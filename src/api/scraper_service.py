import time
import logging
from typing import List, Dict, Any
from dataclasses import asdict
import sys
import os

# Add src to python path to allow for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agent.main import generate_leads
from src.agent.storage.excel_writer import ExcelWriter
from src.agent.config import EXCEL_FILENAME

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_scrapers_service(query: str, selected_scrapers: List[str], confidence_threshold: float) -> Dict[str, Any]:
    """
    A service function that encapsulates the scraper execution logic.
    - Handles scraper execution
    - Logs execution time
    - Manages errors and empty results
    - Ensures safe creation of the Excel file
    """
    start_time = time.time()
    logging.info(f"Starting scraper service for query: '{query}'")

    try:
        # 1. Run the core lead generation logic
        result = generate_leads(
            query=query,
            selected_scraper_names=selected_scrapers,
            confidence_threshold=confidence_threshold
        )
        leads = result.get("leads", [])

        # 2. Handle the results
        if not leads:
            logging.info("Scraping completed with no leads found.")
            return {
                "status": "success",
                "message": "No leads found for the given query.",
                "data": {"leads": []}
            }

        # 3. Save to Excel safely
        try:
            excel_writer = ExcelWriter(filename=EXCEL_FILENAME)
            excel_writer.save(leads)
            logging.info(f"Successfully saved leads to {EXCEL_FILENAME}")
        except Exception as e:
            logging.error(f"Failed to save leads to Excel: {e}")
            # Decide if this should be a critical failure or just a warning
            # For now, we'll log the error and continue to return the leads data
            pass # Or raise a specific internal error

        # 4. Format response
        leads_as_dicts = [asdict(lead) for lead in leads]

        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        logging.info(f"Scraper service finished in {execution_time} seconds.")

        return {
            "status": "success",
            "message": f"Successfully retrieved {len(leads_as_dicts)} leads.",
            "data": {
                "leads": leads_as_dicts,
                "execution_time_seconds": execution_time
            }
        }

    except Exception as e:
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        logging.error(f"An error occurred in the scraper service after {execution_time} seconds: {e}", exc_info=True)
        return {
            "status": "error",
            "message": "An unexpected error occurred during the scraping process.",
            "error_details": str(e),
            "execution_time_seconds": execution_time
        }

if __name__ == '__main__':
    # Example usage for testing the service directly
    test_query = "restaurants in new york"
    test_scrapers = ["GoogleMapsScraper"] # Example scraper

    # Mock discover_scrapers if needed or ensure your environment is set up
    print("Testing scraper service...")
    response = run_scrapers_service(test_query, test_scrapers, 0.0)
    print("--- Service Response ---")
    import json
    print(json.dumps(response, indent=2))
    print("------------------------")
