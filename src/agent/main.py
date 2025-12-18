from src.agent.storage.excel_storage import ExcelStorage
from src.agent.config import SOURCES

def main():
    """Main execution function for the agent."""
    all_leads = []
    for source_class in SOURCES:
        source_instance = source_class()
        leads = source_instance.scrape()
        all_leads.extend(leads)

    if all_leads:
        storage = ExcelStorage("data/leads.xlsx")
        storage.save(all_leads)
        print(f"Successfully scraped {len(all_leads)} leads.")
    else:
        print("No leads were scraped.")

if __name__ == "__main__":
    main()
