from scrapers.registry import scraper_registry
from errors import ScraperError
import asyncio

class ScrapeOrchestrator:
    async def run(self, query: str) -> dict:
        results = {}
        pagination = {}
        errors = []

        platforms_to_run = ["google_search", "google_maps", "facebook", "linkedin", "instagram"]

        tasks = []
        for platform in platforms_to_run:
            scraper = scraper_registry.get_scraper(platform)
            tasks.append(self._run_scraper(scraper, query))

        all_results = await asyncio.gather(*tasks)

        for platform, platform_results, platform_pagination, error in all_results:
            if error:
                errors.append(error)
            else:
                results[platform] = platform_results
                pagination[platform] = platform_pagination is not None

        return {
            "query": query,
            "platforms": results,
            "pagination": pagination,
            "errors": errors
        }

    async def _run_scraper(self, scraper, query):
        try:
            platform_results, platform_pagination = await scraper.scrape(query)
            return scraper.platform, platform_results, platform_pagination, None
        except ScraperError as e:
            return scraper.platform, None, None, e.to_dict()
        except Exception as e:
            error_details = f"An unexpected error occurred: {type(e).__name__} - {e}"
            unexpected_error = ScraperError(
                platform=scraper.platform,
                reason=error_details,
                recommended_action="Manual review required."
            )
            print(f"An unexpected error occurred for platform '{scraper.platform}': {e}")
            return scraper.platform, None, None, unexpected_error.to_dict()

scrape_orchestrator = ScrapeOrchestrator()
