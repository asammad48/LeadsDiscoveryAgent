import pandas as pd
import os
import time
from orchestrator import scrape_orchestrator
import scrapers # Import the scrapers package to ensure registration

class ScraperService:
    def run_scraper(self, query: str) -> dict:
        print(f"Running scrapers for query: {query}")

        aggregated_results = scrape_orchestrator.run(query)

        all_results = []
        for platform, platform_results in aggregated_results['platforms'].items():
            all_results.extend(platform_results)

        if all_results:
            df = pd.DataFrame(all_results)
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            timestamp = int(time.time())
            filename = f"{output_dir}/aggregated_output_{timestamp}.xlsx"
            df.to_excel(filename, index=False)
            aggregated_results['filename'] = os.path.basename(filename)
        else:
            aggregated_results['filename'] = None

        return aggregated_results

    def get_excel_path(self, filename: str) -> str:
        return f"output/{filename}"

scraper_service = ScraperService()
