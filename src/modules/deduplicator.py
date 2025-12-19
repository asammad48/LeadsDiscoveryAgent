import copy
from typing import List, Dict, Any, Optional, Set
from agent.models.lead import Lead

class Deduplicator:
    """A class to deduplicate and merge a list of Lead objects."""

    def deduplicate(self, leads: List[Lead]) -> List[Lead]:
        """
        Deduplicates a list of leads based on website, or a combination of
        business name and city as a fallback. Merges duplicate entries,
        handling transitive relationships.
        """
        if not leads:
            return []

        # Union-Find data structure
        parent = list(range(len(leads)))
        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]
        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_j] = root_i

        # Map keys (websites, company/city tuples) to lead indices
        key_to_index: Dict[Any, int] = {}

        for i, lead in enumerate(leads):
            # Check for website key
            if lead.website:
                if lead.website in key_to_index:
                    union(i, key_to_index[lead.website])
                else:
                    key_to_index[lead.website] = i

            # Check for company/city key
            company_city = (lead.company, lead.city)
            if company_city in key_to_index:
                union(i, key_to_index[company_city])
            else:
                key_to_index[company_city] = i

        # Group leads by their root parent
        merged_leads_groups: Dict[int, List[Lead]] = {}
        for i, lead in enumerate(leads):
            root = find(i)
            if root not in merged_leads_groups:
                merged_leads_groups[root] = []
            merged_leads_groups[root].append(lead)

        # Merge the leads within each group
        final_leads: List[Lead] = []
        for group in merged_leads_groups.values():
            if not group:
                continue

            merged_lead = copy.deepcopy(group[0])
            for i in range(1, len(group)):
                merged_lead = self._merge_leads(merged_lead, group[i])
            final_leads.append(merged_lead)

        return final_leads

    def _merge_comma_separated_fields(self, field1: Optional[str], field2: Optional[str]) -> Optional[str]:
        """
        Merges two comma-separated string fields into a single sorted,
        comma-separated string with unique values.
        """
        if not field1 and not field2:
            return None

        set1 = set(s.strip() for s in field1.split(',')) if field1 else set()
        set2 = set(s.strip() for s in field2.split(',')) if field2 else set()

        set1.discard('')
        set2.discard('')

        merged_set = sorted(list(set1.union(set2)))
        return ", ".join(merged_set) if merged_set else None

    def _merge_leads(self, lead1: Lead, lead2: Lead) -> Lead:
        """
        Merges two Lead objects into one, prioritizing non-null values.
        Appends unique values for 'source' and 'linkedin_profile'.
        Returns a new merged Lead object.
        """
        merged_lead = copy.deepcopy(lead1)

        # Merge 'source' and 'linkedin_profile'
        merged_lead.source = self._merge_comma_separated_fields(lead1.source, lead2.source)
        merged_lead.linkedin_profile = self._merge_comma_separated_fields(lead1.linkedin_profile, lead2.linkedin_profile)

        # Merge other fields, prioritizing existing data over None
        for field in ['name', 'company', 'city', 'title', 'email', 'phone', 'website', 'notes']:
            if getattr(merged_lead, field) is None and getattr(lead2, field) is not None:
                setattr(merged_lead, field, getattr(lead2, field))

        return merged_lead
