import os
import sys
import glob
import importlib
from typing import List

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agent.models.lead import Lead
from src.modules.intent_parser import IntentParser
from src.modules.keyword_expander import KeywordExpander
from src.modules.scorer import Scorer
from src.modules.deduplicator import Deduplicator
from src.agent.storage.excel_writer import ExcelWriter
from src.agent.sources.base_source import BaseSource

def discover_scrapers() -> List[BaseSource]:
    """Dynamically discovers all scraper classes in the sources directory."""
    scrapers = []
    sources_path = os.path.join(os.path.dirname(__file__), 'sources')
    for file in glob.glob(os.path.join(sources_path, '*_scraper.py')):
        module_name = os.path.basename(file)[:-3]
        module = importlib.import_module(f'src.agent.sources.{module_name}')
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, type) and issubclass(attribute, BaseSource) and attribute is not BaseSource:
                scrapers.append(attribute)
    return scrapers

def run_query(query: str):
    """Runs the entire lead generation process for a given query."""
    print(f"--- Running query: '{query}' ---")

    # 1. Parse intent
    print("1. Parsing intent...")
    parser = IntentParser()
    intent = parser.parse(query)
    print(f"   - Intent: {intent}")

    # 2. Expand keywords
    print("2. Expanding keywords...")
    expander = KeywordExpander()
    expanded_keywords = expander.expand(intent)
    print(f"   - Expanded keywords: {expanded_keywords['expanded_keywords'][:5]}...")

    # 3. Scrape all platforms
    print("3. Scraping all platforms...")
    scraper_classes = discover_scrapers()
    all_leads = []
    platform_queries = expanded_keywords.get('platform_specific', {})

    for scraper_class in scraper_classes:
        scraper_name = scraper_class.__name__
        platform_name = scraper_name.replace('Scraper', '').lower()

        # Map scraper names to platform keys used in KeywordExpander
        if 'linkedin' in platform_name:
            platform_name = 'linkedin'
        elif 'google' in platform_name:
            platform_name = 'google'
        elif 'facebook' in platform_name:
            platform_name = 'facebook'
        elif 'instagram' in platform_name:
            platform_name = 'instagram'

        queries = platform_queries.get(platform_name, [query]) # Fallback to original query

        print(f"   - Running scraper: {scraper_name} for platform '{platform_name}'")

        for q in queries:
            try:
                # Instantiate the scraper with the specific query
                scraper_instance = scraper_class(query=q)

                # Handle Selenium scrapers that need a context manager
                if hasattr(scraper_instance, '__enter__'):
                    with scraper_instance as scraper:
                        leads = scraper.scrape()
                else:
                    leads = scraper_instance.scrape()

                all_leads.extend(leads)
                if leads:
                    print(f"      -> Found {len(leads)} leads from query: '{q[:60]}...'")

            except TypeError as e:
                # This catches scrapers with constructors not matching `__init__(self, query)`
                # This is a temporary measure to allow for incremental refactoring of scrapers.
                if 'required positional argument' in str(e) or 'unexpected keyword argument' in str(e):
                     print(f"   - SKIPPING scraper: {scraper_name} due to incompatible constructor.")
                else:
                     print(f"   - ERROR instantiating {scraper_name}: {e}")
                break # Stop trying queries for this incompatible scraper
            except Exception as e:
                print(f"   - ERROR running scraper {scraper_name} with query '{q}': {e}")

    print(f"   - Scraped a total of {len(all_leads)} leads.")

    # 4. Score leads
    print("4. Scoring leads...")
    scorer = Scorer()
    for lead in all_leads:
        lead.confidence_score = scorer.score(lead, expanded_keywords, intent)
    print(f"   - Scored {len(all_leads)} leads.")

    # 5. Deduplicate
    print("5. Deduplicating leads...")
    deduplicator = Deduplicator()
    deduplicated_leads = deduplicator.deduplicate(all_leads)
    print(f"   - Deduplicated to {len(deduplicated_leads)} leads.")

    # 6. Save to Excel
    print("6. Saving to Excel...")
    excel_writer = ExcelWriter(filename="leads_output.xlsx")
    excel_writer.save(deduplicated_leads)
    print("   - Saved to leads_output.xlsx")

    # 7. Print summary report
    print("\n--- Summary Report ---")
    print(f"Query: '{query}'")
    print(f"Parsed Intent: {intent}")
    print(f"Total Leads Scraped: {len(all_leads)}")
    print(f"Unique Leads Found: {len(deduplicated_leads)}")
    print("--- End of Report ---\n")

def main():
    """Main execution function."""
    queries = [
        "Hotels in England that may need POS",
        "Restaurants in London looking for a new website",
        "Software companies in San Francisco"
    ]
    for query in queries:
        run_query(query)

if __name__ == "__main__":
    main()
