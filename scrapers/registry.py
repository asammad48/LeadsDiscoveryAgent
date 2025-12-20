from scrapers.base import BaseScraper

class ScraperRegistry:
    def __init__(self):
        self._scrapers = {}

    def register(self, scraper_class: type[BaseScraper]):
        if not issubclass(scraper_class, BaseScraper):
            raise TypeError("Registered class must be a subclass of BaseScraper.")
        if not hasattr(scraper_class, 'platform') or not scraper_class.platform:
            raise AttributeError("Scraper class must have a 'platform' attribute.")

        platform = scraper_class.platform
        if platform in self._scrapers:
            raise ValueError(f"Scraper for platform '{platform}' is already registered.")

        self._scrapers[platform] = scraper_class()
        print(f"Registered scraper for platform: {platform}")

    def get_scraper(self, platform: str) -> BaseScraper:
        scraper = self._scrapers.get(platform)
        if not scraper:
            raise ValueError(f"No scraper registered for platform: {platform}")
        return scraper

    @property
    def supported_platforms(self) -> list[str]:
        return list(self._scrapers.keys())

# Global registry instance
scraper_registry = ScraperRegistry()

def register_scraper(cls: type[BaseScraper]):
    """A class decorator to register scrapers."""
    scraper_registry.register(cls)
    return cls
