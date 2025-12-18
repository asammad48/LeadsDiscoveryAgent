import re
from typing import Dict, Any, List

class IntentParser:
    """
    Parses a natural language query to extract structured information.
    """

    def __init__(self, llm_hook: Any = None):
        """
        Initializes the IntentParser.
        Args:
            llm_hook: An optional Language Model hook for more advanced parsing.
        """
        self.llm_hook = llm_hook
        # Simple rule-based keywords
        self.industry_keywords = ["hotels", "restaurants", "clinics", "software"]
        self.pain_point_keywords = ["pos", "website", "marketing", "seo"]
        self.location_terminators = ["that", "looking", "for", "who", "with"]

    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parses the query to extract intent.
        Args:
            query: The natural language query.
        Returns:
            A dictionary containing the parsed information.
        """
        if self.llm_hook:
            # If an LLM hook is provided, use it for parsing
            return self.llm_hook.parse(query)
        else:
            # Otherwise, use the rule-based approach
            return self._parse_rule_based(query)

    def _parse_rule_based(self, query: str) -> Dict[str, Any]:
        """
        A simple rule-based parser.
        """
        words = query.lower().split()
        result: Dict[str, Any] = {
            "industry": None,
            "location": None,
            "business_type": None,
            "pain_point_need": None,
            "base_keywords": [],
        }

        # 1. Extract Location
        try:
            in_index = words.index("in")
            location_words = words[in_index + 1:]
            terminator_index = len(location_words) # Default to end of list
            for i, word in enumerate(location_words):
                if word in self.location_terminators:
                    terminator_index = i
                    break
            result["location"] = " ".join(location_words[:terminator_index])
        except ValueError:
            result["location"] = None


        # 2. Extract Industry & Business Type
        for word in words:
            if word in self.industry_keywords:
                result["industry"] = word
                result["business_type"] = word  # For now, we'll use the same
                break

        # 3. Extract Pain Point / Need
        for word in words:
            if word in self.pain_point_keywords:
                result["pain_point_need"] = word
                break

        # 4. Determine Base Keywords
        # This is a simplistic approach: take all nouns or unrecognized terms.
        # For this example, we'll just take the industry if found.
        if result["industry"]:
            result["base_keywords"].append(result["industry"])
        if result["location"]:
            result["base_keywords"].append(result["location"])


        return result

# Example Usage
if __name__ == "__main__":
    parser = IntentParser()

    # Example 1
    query1 = "Hotels in England that may need POS"
    parsed_intent1 = parser.parse(query1)
    print(f"Query: '{query1}'")
    print(f"Parsed Intent: {parsed_intent1}")
    print("-" * 20)

    # Example 2
    query2 = "Restaurants in London looking for a new website"
    parsed_intent2 = parser.parse(query2)
    print(f"Query: '{query2}'")
    print(f"Parsed Intent: {parsed_intent2}")
    print("-" * 20)

    # Example 3
    query3 = "Software companies in San Francisco"
    parsed_intent3 = parser.parse(query3)
    print(f"Query: '{query3}'")
    print(f"Parsed Intent: {parsed_intent3}")
    print("-" * 20)
