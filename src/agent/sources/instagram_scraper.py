import instaloader
import logging
import re
import time
from typing import List, Optional, Set
from src.agent.models.lead import Lead
from src.agent.sources.base_source import BaseSource

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstagramScraper(BaseSource):
    """
    A scraper for fetching lead data from public Instagram profiles using usernames or hashtags.
    """

    def __init__(self, usernames: Optional[List[str]] = None, hashtags: Optional[List[str]] = None, max_profiles_per_hashtag: int = 20):
        self.loader = instaloader.Instaloader()
        self.usernames_to_scrape = set(usernames) if usernames else set()
        self.hashtags_to_scrape = set(hashtags) if hashtags else set()
        self.max_profiles_per_hashtag = max_profiles_per_hashtag

    def _get_profiles_from_hashtags(self) -> Set[str]:
        """Discover usernames from hashtag search."""
        discovered_usernames = set()
        if not self.hashtags_to_scrape:
            return discovered_usernames

        for hashtag in self.hashtags_to_scrape:
            logging.info(f"Scraping hashtag: #{hashtag}")
            try:
                posts = instaloader.Hashtag.from_name(self.loader.context, hashtag).get_posts()
                count = 0
                for post in posts:
                    if count >= self.max_profiles_per_hashtag:
                        break
                    discovered_usernames.add(post.owner_username)
                    count += 1
                    time.sleep(1) # Rate limiting
            except Exception as e:
                logging.error(f"Could not scrape hashtag #{hashtag}: {e}")
        return discovered_usernames

    def _parse_email(self, text: str) -> Optional[str]:
        """Extracts the first email found in a string."""
        match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        return match.group(0).rstrip('.') if match else None

    def _parse_website(self, text: str) -> Optional[str]:
        """Extracts the first URL found in a string."""
        match = re.search(r'(https?://[^\s]+)', text)
        return match.group(0) if match else None

    def scrape(self) -> List[Lead]:
        """
        Scrapes lead data from Instagram profiles.

        - Discovers profiles from hashtags.
        - Scrapes profiles from a direct list of usernames.
        - Parses bio for contact info and creates Lead objects.

        Returns:
            A list of Lead objects.
        """
        all_leads = []
        target_usernames = self.usernames_to_scrape.union(self._get_profiles_from_hashtags())

        if not target_usernames:
            logging.info("No usernames to scrape.")
            return []

        logging.info(f"Found {len(target_usernames)} unique profiles to scrape.")

        for username in target_usernames:
            logging.info(f"Scraping profile: {username}")
            try:
                profile = instaloader.Profile.from_username(self.loader.context, username)

                # Data Extraction
                bio = profile.biography
                email = self._parse_email(bio)
                website = profile.external_url or self._parse_website(bio)
                business_category = profile.business_category_name

                # Construct notes
                notes = f"Bio: {bio}\nBusiness Category: {business_category}"

                lead = Lead(
                    name=profile.full_name or username,
                    company=profile.full_name or username,
                    email=email,
                    website=website,
                    source='Instagram',
                    notes=notes.strip()
                )
                all_leads.append(lead)

                # Rate limiting between profile scrapes
                time.sleep(2)

            except instaloader.exceptions.ProfileNotFound:
                logging.warning(f"Profile not found: {username}")
            except Exception as e:
                logging.error(f"An error occurred while scraping profile '{username}': {e}")
                time.sleep(10) # Longer sleep on error

        return all_leads
