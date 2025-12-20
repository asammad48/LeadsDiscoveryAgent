from facebook_scraper import get_posts
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

@register_scraper
class FacebookScraper(BaseScraper):
    platform = "facebook"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        try:
            posts = list(get_posts(query, pages=1))
        except Exception:
            raise NoResultsFoundError(self.platform)

        if not posts:
            raise NoResultsFoundError(self.platform)

        results = []
        for post in posts:
            results.append({
                'business_name': post['username'],
                'description/snippet': post['text'],
                'platform': self.platform,
                'source_url': post['post_url'],
            })

        return results, None

    def _parse_search_results(self, soup) -> list[str]:
        return []

    def _parse_profile_page(self, soup, source_url: str) -> dict:
        return {}
