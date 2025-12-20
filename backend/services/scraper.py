from orchestrator import scrape_orchestrator
from fuzzywuzzy import process
import asyncio

class ScraperService:
    async def run_scraper(self, query: str) -> dict:
        print(f"Running authoritative scraper for query: {query}")

        raw_results = await scrape_orchestrator.run(query)

        merged_data = self._merge_and_deduplicate(raw_results['platforms'])

        raw_results['filename'] = None
        raw_results['platforms'] = merged_data

        return raw_results

    def _merge_and_deduplicate(self, platforms_data: dict) -> list[dict]:
        google_maps_results = platforms_data.get('google_maps', [])
        if not google_maps_results:
            print("No Google Maps results found. No authoritative data to build upon. Returning empty list.")
            return []

        authoritative_leads = {lead['business_name'].lower(): lead for lead in google_maps_results}

        print(f"Found {len(authoritative_leads)} authoritative leads from Google Maps.")

        final_results = {}

        for name, lead_data in authoritative_leads.items():
            final_results[name] = {
                "business_name": lead_data['business_name'],
                "website": lead_data.get('website'),
                "phone": lead_data.get('phone'),
                "address": lead_data.get('address'),
                "sources": {"google_maps": lead_data['source_url']}
            }

        for platform, results in platforms_data.items():
            if platform == 'google_maps' or not results:
                continue

            for lead in results:
                lead_name = lead['business_name'].lower()

                best_match, score = process.extractOne(lead_name, final_results.keys())

                if score > 85:
                    print(f"  > Merging '{lead['business_name']}' ({platform}) into '{best_match}' (Score: {score})")
                    final_results[best_match]['sources'][platform] = lead['source_url']
                else:
                    print(f"  > Discarding low-confidence lead '{lead['business_name']}' from {platform} (Score: {score})")

        return list(final_results.values())

    def get_excel_path(self, filename: str) -> str:
        return f"output/{filename}"

scraper_service = ScraperService()
