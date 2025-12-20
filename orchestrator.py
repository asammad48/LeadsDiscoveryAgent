from scrapers.registry import scraper_registry
from errors import ScraperError

class ScrapeOrchestrator:
    def run(self, query: str) -> dict:
        results = {}
        pagination = {}
        errors = []

        for platform, scraper in scraper_registry._scrapers.items():
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
                print(f"An unexpected error occurred for platform '{platform}': {e}")
                errors.append({
                    "platform": platform,
                    "reason": "An unexpected error occurred.",
                    "action_required": "Manual review"
                })

        return {
            "query": query,
            "platforms": results,
            "pagination": pagination,
            "errors": errors
        }

scrape_orchestrator = ScrapeOrchestrator()
