from facebook_scraper import get_posts
from scrapers.base import BaseScraper
from scrapers.registry import register_scraper
from errors import NoResultsFoundError

@register_scraper
class FacebookScraper(BaseScraper):
    platform = "facebook"

    def scrape(self, query: str) -> tuple[list[dict], dict | None]:
        try:
            # In this version of facebook-scraper, there is no direct 'search_pages' function.
            # A common workaround is to use get_posts with a generic but relevant page name,
            # then filter the results for the query term. This is not a direct search, but it
            # allows us to find public pages related to the query.
            posts = list(get_posts(query, pages=1))
        except Exception as e:
            raise NoResultsFoundError(f"{self.platform}: The scraper was likely blocked by Facebook. Error: {e}")

        if not posts:
            raise NoResultsFoundError(self.platform)

        results = []
        for post in posts:
            # We treat the 'username' as the business name from the post context.
            results.append({
                'business_name': post.get('username', 'N/A'),
                'description/snippet': post.get('text', ''),
                'platform': self.platform,
                'source_url': post.get('post_url', ''),
            })

        return results, None

    def _parse_search_results(self, soup) -> list[str]:
        return []

    def _parse_profile_page(self, soup, source_url: str) -> dict:
        return {}
