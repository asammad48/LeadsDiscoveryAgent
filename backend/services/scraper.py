import pandas as pd
import os
from google_html_parser import parse_google_search_html

class ScraperService:
    def run_scraper(self, query: str) -> tuple[list, str]:
        print(f"Parsing HTML for query: {query}")

        try:
            with open('google_search_results.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            print("Error: google_search_results.html not found.")
            return [], ""

        results, next_page_url = parse_google_search_html(html_content)

        df = pd.DataFrame(results)

        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename = f"{output_dir}/parsed_output.xlsx"
        df.to_excel(filename, index=False)

        if next_page_url:
            with open(f"{output_dir}/next_page.txt", "w") as f:
                f.write(next_page_url)

        return df.to_dict(orient='records'), filename

    def get_excel_path(self, filename: str) -> str:
        return f"output/{filename}"

scraper_service = ScraperService()
