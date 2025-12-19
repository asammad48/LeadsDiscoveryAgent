from typing import Dict, Any, List
import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.models.lead import Lead

class Scorer:
    """
    Scores leads based on relevance to a given intent.
    """

    KEYWORD_WEIGHT = 0.4
    LOCATION_WEIGHT = 0.2
    INDUSTRY_WEIGHT = 0.2
    CONTACT_INFO_WEIGHT = 0.1
    PLATFORM_RELIABILITY_WEIGHT = 0.1

    PLATFORM_RELIABILITY_SCORES = {
        "linkedin": 90,
        "google": 80,
        "facebook": 70,
        "instagram": 60,
        "default": 50,
    }

    def score(self, lead: Lead, expanded_keywords: Dict[str, Any], intent: Dict[str, Any]) -> int:
        """
        Calculates a confidence score for a single lead.

        The scoring formula is a weighted average of the following factors:
        - Keyword Matches: 40%
        - Location Match: 20%
        - Industry Relevance: 20%
        - Presence of Website/Email: 10%
        - Platform Reliability: 10%
        """
        keyword_score = self._calculate_keyword_score(lead, expanded_keywords)
        location_score = self._calculate_location_score(lead, intent)
        industry_score = self._calculate_industry_score(lead, intent)
        contact_info_score = self._calculate_contact_info_score(lead)
        platform_reliability_score = self._calculate_platform_reliability_score(lead)

        final_score = (
            keyword_score * self.KEYWORD_WEIGHT +
            location_score * self.LOCATION_WEIGHT +
            industry_score * self.INDUSTRY_WEIGHT +
            contact_info_score * self.CONTACT_INFO_WEIGHT +
            platform_reliability_score * self.PLATFORM_RELIABILITY_WEIGHT
        )

        return int(final_score)

    def filter_leads(self, leads: List[Lead], expanded_keywords: Dict[str, Any], intent: Dict[str, Any], threshold: int) -> List[Lead]:
        """
        Filters a list of leads based on a confidence score threshold.
        """
        return [lead for lead in leads if self.score(lead, expanded_keywords, intent) >= threshold]

    def _calculate_keyword_score(self, lead: Lead, expanded_keywords: Dict[str, Any]) -> int:
        """
        Calculates the keyword match score.
        """
        score = 0
        lead_text = f"{lead.name} {lead.company} {lead.title} {lead.notes}".lower()

        for keyword in expanded_keywords.get("expanded_keywords", []):
            if keyword in lead_text:
                score += 1

        # Normalize the score
        if len(expanded_keywords.get("expanded_keywords", [])) > 0:
            return (score / len(expanded_keywords.get("expanded_keywords", []))) * 100
        return 0

    def _calculate_location_score(self, lead: Lead, intent: Dict[str, Any]) -> int:
        """
        Calculates the location match score.
        """
        lead_text = f"{lead.name} {lead.company} {lead.title} {lead.notes}".lower()
        if intent.get("location") and intent.get("location") in lead_text:
            return 100
        return 0

    def _calculate_industry_score(self, lead: Lead, intent: Dict[str, Any]) -> int:
        """
        Calculates the industry match score.
        """
        lead_text = f"{lead.name} {lead.company} {lead.title} {lead.notes}".lower()
        if intent.get("industry") and intent.get("industry") in lead_text:
            return 100
        return 0

    def _calculate_contact_info_score(self, lead: Lead) -> int:
        """
        Calculates the contact info score.
        """
        if lead.website or lead.email:
            return 100
        return 0

    def _calculate_platform_reliability_score(self, lead: Lead) -> int:
        """
        Calculates the platform reliability score.
        """
        return self.PLATFORM_RELIABILITY_SCORES.get(lead.source, self.PLATFORM_RELIABILITY_SCORES["default"])
