from orchestrator import scrape_orchestrator
from fuzzywuzzy import process

class ScraperService:
    """
    This service orchestrates the scraping process and enforces the authoritative
    data aggregation and deduplication logic.
    """

    def run_scraper(self, query: str) -> dict:
        print(f"Running authoritative scraper for query: {query}")

        # Run all scrapers to gather raw data
        raw_results = scrape_orchestrator.run(query)

        # Process and merge the results according to the new business rules
        merged_data = self._merge_and_deduplicate(raw_results['platforms'])

        # We no longer generate an Excel file; the primary output is the structured JSON.
        raw_results['filename'] = None
        raw_results['platforms'] = merged_data # Replace raw data with clean, merged data

        return raw_results

    def _merge_and_deduplicate(self, platforms_data: dict) -> list[dict]:
        """
        Implements the core business logic:
        1. Google Maps is the source of truth.
        2. Other platforms are merged into Google Maps entries.
        3. Any lead without a matching Google Maps entry is discarded.
        """
        google_maps_results = platforms_data.get('google_maps', [])
        if not google_maps_results:
            print("No Google Maps results found. No authoritative data to build upon. Returning empty list.")
            return []

        # Create a dictionary for easy lookup of Google Maps results by business name
        authoritative_leads = {lead['business_name'].lower(): lead for lead in google_maps_results}

        print(f"Found {len(authoritative_leads)} authoritative leads from Google Maps.")

        # Initialize the final merged data structure
        final_results = {}

        # First pass: build the final structure from Google Maps data
        for name, lead_data in authoritative_leads.items():
            final_results[name] = {
                "business_name": lead_data['business_name'],
                "website": lead_data.get('website'),
                "phone": lead_data.get('phone'),
                "address": lead_data.get('address'),
                "sources": {"google_maps": lead_data['source_url']}
            }

        # Second pass: iterate through other platforms and merge them
        for platform, results in platforms_data.items():
            if platform == 'google_maps':
                continue # Skip, as we've already processed it

            for lead in results:
                lead_name = lead['business_name'].lower()

                # Use fuzzy matching to find the best match in our authoritative list
                best_match, score = process.extractOne(lead_name, final_results.keys())

                # A high score (e.g., > 85) indicates a confident match
                if score > 85:
                    print(f"  > Merging '{lead['business_name']}' ({platform}) into '{best_match}' (Score: {score})")
                    final_results[best_match]['sources'][platform] = lead['source_url']
                else:
                    print(f"  > Discarding low-confidence lead '{lead['business_name']}' from {platform} (Score: {score})")

        return list(final_results.values())

    def get_excel_path(self, filename: str) -> str:
        # This is no longer used but kept for API compatibility.
        return f"output/{filename}"

scraper_service = ScraperService()
