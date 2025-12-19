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
    for scraper_class in scraper_classes:
        # Mocking scraper instantiation and execution for this example
        print(f"   - Running scraper: {scraper_class.__name__}")
        # In a real scenario, you would instantiate and call scrape:
        # scraper_instance = scraper_class(...)
        # leads = scraper_instance.scrape()
        # For this example, we'll create mock leads
        mock_leads = [
            Lead(name=f"{scraper_class.__name__} Lead 1", company=f"Company for {intent['industry']}", website=f"www.{intent['industry']}1.com", source=scraper_class.__name__),
            Lead(name=f"{scraper_class.__name__} Lead 2", company=f"Another {intent['industry']} Corp", website=f"www.another{intent['industry']}.com", source=scraper_class.__name__)
        ]
        all_leads.extend(mock_leads)
    print(f"   - Scraped {len(all_leads)} leads.")

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
