import re
import logging
from typing import List, Optional
from facebook_scraper import get_posts, get_profile, get_group_info
from src.agent.models.lead import Lead
from src.agent.sources.base_source import BaseSource

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FacebookPublicScraper(BaseSource):
    """
    A scraper for fetching lead data from public Facebook pages or groups.
    It scrapes the main profile/info, and scans posts for contact details,
    optionally filtering by keywords.
    """

    def __init__(self, target_id: str, target_type: str = 'page', keywords: Optional[List[str]] = None, pages_to_scrape: int = 5):
        self.target_id = target_id
        self.target_type = target_type.lower()
        self.keywords = [k.lower() for k in keywords] if keywords else []
        self.pages_to_scrape = pages_to_scrape

        if self.target_type not in ['page', 'group']:
            raise ValueError("target_type must be either 'page' or 'group'")

    def scrape(self) -> List[Lead]:
        """
        Scrapes leads from a Facebook page or group.

        This method fetches the main profile/group information to create a primary
        lead, then scrapes recent posts to find additional contact information,
        filtering by keywords if provided.

        Returns:
            A list containing a single Lead object if successful, or an empty list.
        """
        try:
            # 1. Scrape the main profile or group info
            info = None
            if self.target_type == 'page':
                info = get_profile(self.target_id)
                name = info.get('Name', self.target_id)
                notes = info.get('About', '')
                website = info.get('Website')
            else: # group
                info = get_group_info(self.target_id)
                name = info.get('name', self.target_id)
                notes = f"Facebook Group. Members: {info.get('members')}"
                website = None # Groups don't have a website field

            if not info:
                logging.warning(f"Could not retrieve info for {self.target_type}: {self.target_id}")
                return []

            lead = Lead(name=name, company=name, website=website, notes=notes, source='Facebook')

            # 2. Scrape posts for contact info
            all_emails = set()
            all_phones = set()

            if self.target_type == 'group':
                post_iterator = get_posts(group=self.target_id, pages=self.pages_to_scrape)
            else:  # page
                post_iterator = get_posts(account=self.target_id, pages=self.pages_to_scrape)

            for post in post_iterator:
                post_text = post.get('text', '')
                if not post_text:
                    continue

                post_text_lower = post_text.lower()
                if self.keywords and not any(key in post_text_lower for key in self.keywords):
                    continue

                emails = re.findall(r'[\w\.-]+@[\w\.-]+', post_text)
                all_emails.update(emails)

                phones = re.findall(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', post_text)
                all_phones.update(phones)

            # Deterministic contact assignment
            if all_emails:
                lead.email = sorted(list(all_emails))[0]
            if all_phones:
                lead.phone = sorted(list(all_phones))[0]

            return [lead]

        except Exception as e:
            logging.error(f"An error occurred while scraping Facebook {self.target_type} '{self.target_id}': {e}")
            return []
