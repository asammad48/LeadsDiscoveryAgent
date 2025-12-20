from scrapers.registry import scraper_registry
from errors import ScraperError

class ScrapeOrchestrator:
    def run(self, query: str) -> dict:
        results = {}
        pagination = {}
        errors = []

        # Use a controlled list of platforms to run
        platforms_to_run = ["google_search", "google_maps", "facebook", "linkedin", "instagram"]

        for platform in platforms_to_run:
            scraper = scraper_registry.get_scraper(platform)
            try:
                platform_results, platform_pagination = scraper.scrape(query)
                results[platform] = platform_results
                if platform_pagination:
                    pagination[platform] = True
                else:
                    pagination[platform] = False
            except ScraperError as e:
                errors.append(e.to_dict())
            except Exception as e:
                # Wrap unexpected errors in a ScraperError for consistent reporting
                error_details = f"An unexpected error occurred: {type(e).__name__} - {e}"
                unexpected_error = ScraperError(
                    platform=platform,
                    reason=error_details,
                    recommended_action="Manual review required. The scraper's underlying library may have failed."
                )
                errors.append(unexpected_error.to_dict())
                print(f"An unexpected error occurred for platform '{platform}': {e}")

        return {
            "query": query,
            "platforms": results,
            "pagination": pagination,
            "errors": errors
        }

scrape_orchestrator = ScrapeOrchestrator()
