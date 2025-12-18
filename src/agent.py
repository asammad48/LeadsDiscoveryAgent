from modules.web_search import search_web
from modules.excel_storage import ExcelStorage

class LeadDiscoveryAgent:
    def __init__(self):
        self.storage = ExcelStorage()

    def discover_leads(self, query: str):
        print(f"Searching for leads with query: '{query}'")

        # Perform the web search
        search_results = search_web(query)

        if not search_results:
            print("No leads found.")
            return

        # Format the results for storage
        leads = [{"url": url, "source": "web_search"} for url in search_results]

        # Save the leads to an Excel file
        filename = f"{query.replace(' ', '_')}_leads.xlsx"
        self.storage.save_to_excel(leads, filename)

        print(f"Discovered {len(leads)} leads. Saved to data/{filename}")

if __name__ == '__main__':
    agent = LeadDiscoveryAgent()
    agent.discover_leads("Python developers in San Francisco")
