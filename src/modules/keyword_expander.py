from typing import Dict, Any, List

class KeywordExpander:
    """
    Expands a parsed intent into a rich set of keywords, tags, and search queries.
    """

    def __init__(self):
        """
        Initializes the KeywordExpander with platform-specific maps and synonyms.
        """
        self.synonym_map = {
            "pos": ["point of sale", "payment processing", "merchant services", "cash register system"],
            "website": ["web development", "online presence", "business website", "ecommerce site"],
            "leads": ["lead generation", "customer acquisition", "sales leads", "prospecting"],
            "hotels": ["hospitality", "lodging", "resorts", "inns"],
            "clinics": ["medical practice", "healthcare facility", "doctors office", "patient care"],
            "call centers": ["customer support", "telemarketing", "contact center", "bpo"],
        }

    def expand(self, parsed_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a parsed intent and returns an expanded dictionary.

        Args:
            parsed_intent: A dictionary containing keys like 'industry', 'location', 'pain_point_need'.

        Returns:
            A dictionary with expanded keywords, hashtags, and platform-specific queries.
        """
        industry = parsed_intent.get("industry", "")
        location = parsed_intent.get("location", "")
        pain_point = parsed_intent.get("pain_point_need", "")

        # --- Synonyms and Keyword Expansion ---
        industry_synonyms = [industry] + self.synonym_map.get(industry, [])
        pain_point_synonyms = [pain_point] + self.synonym_map.get(pain_point, [])

        expanded_keywords = [f"{i} {p}" for i in industry_synonyms for p in pain_point_synonyms]
        if location:
            expanded_keywords.extend([f"{k} in {location}" for k in expanded_keywords])

        # --- Hashtags ---
        hashtags = {f"#{industry}", f"#{pain_point}"}
        if location:
            hashtags.add(f"#{location.replace(' ', '')}")
        hashtags.update([f"#{s.replace(' ', '')}" for s in industry_synonyms])
        hashtags.update([f"#{s.replace(' ', '')}" for s in pain_point_synonyms])

        # --- Platform Specific Queries ---
        platform_specific = {
            "linkedin": self._generate_linkedin_queries(industry, pain_point, location, industry_synonyms, pain_point_synonyms),
            "google": self._generate_google_queries(industry, pain_point, location, expanded_keywords),
            "facebook": self._generate_facebook_queries(industry, pain_point, location, industry_synonyms),
            "instagram": self._generate_instagram_queries(industry, pain_point, location, industry_synonyms),
        }

        return {
            "expanded_keywords": expanded_keywords,
            "synonyms": {
                industry: industry_synonyms,
                pain_point: pain_point_synonyms,
            },
            "hashtags": sorted(list(hashtags)),
            "platform_specific": platform_specific,
        }

    def _generate_linkedin_queries(self, industry: str, pain_point: str, location: str, industry_synonyms: List[str], pain_point_synonyms: List[str]) -> List[str]:
        queries = []
        titles = [f'title:"owner"', f'title:"manager"', f'title:"director"']

        # Dynamically build "OR" clauses for all available synonyms.
        industry_clause = " OR ".join(f'"{s}"' for s in industry_synonyms)
        pain_point_clause = " OR ".join(f'"{s}"' for s in pain_point_synonyms)

        for title in titles:
            query = f'{title} ({industry_clause})'
            if pain_point:
                query += f' ({pain_point_clause})'
            if location:
                query += f' "{location}"'
            queries.append(query)
        return queries

    def _generate_google_queries(self, industry: str, pain_point: str, location: str, expanded_keywords: List[str]) -> List[str]:
        queries = []
        if location:
            # Replace unreliable site:.tld search with a more robust query including the location name.
            queries.append(f'"{industry}" "{pain_point}" "{location}" inurl:"contact"')
        queries.append(f'"{industry} looking for {pain_point}"')
        queries.append(f'intitle:"{industry}" AND ("{pain_point}" OR "{expanded_keywords[0]}")')
        if location:
            queries.append(f'"{location} {industry}" +"{pain_point}"')
        return queries

    def _generate_facebook_queries(self, industry: str, pain_point: str, location: str, industry_synonyms: List[str]) -> List[str]:
        # Focus on finding groups and pages
        queries = [
            f'"{industry_synonyms[0]} group"',
            f'"{industry} owners {location}"',
            f'Pages named "{industry} Professionals"',
        ]
        if pain_point:
            queries.append(f'"{industry} group" "{pain_point}"')
        return queries

    def _generate_instagram_queries(self, industry: str, pain_point: str, location: str, industry_synonyms: List[str]) -> List[str]:
        # Focus on hashtags and bio searches
        queries = [
            f"#{industry}owner",
            f"#{industry.capitalize()}{location.capitalize().replace(' ', '')}",
        ]
        if pain_point:
             queries.append(f'bio:"{industry}" "{pain_point}"')
        return queries

# Example Usage
if __name__ == "__main__":
    expander = KeywordExpander()

    print("--- Example 1: Hotels needing POS ---")
    intent1 = {
        "industry": "hotels",
        "location": "england",
        "pain_point_need": "pos",
    }
    expanded1 = expander.expand(intent1)
    import json
    print(json.dumps(expanded1, indent=2))

    print("\n--- Example 2: Call centers selling leads ---")
    intent2 = {
        "industry": "call centers",
        "location": "usa",
        "pain_point_need": "leads",
    }
    expanded2 = expander.expand(intent2)
    print(json.dumps(expanded2, indent=2))

    print("\n--- Example 3: Clinics needing websites ---")
    intent3 = {
        "industry": "clinics",
        "location": "new york",
        "pain_point_need": "website",
    }
    expanded3 = expander.expand(intent3)
    print(json.dumps(expanded3, indent=2))
