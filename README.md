# Lead Discovery & Scraper Agent

This project is a web application that allows users to discover and scrape leads from various sources. It is built with a modular and extensible architecture that allows for easy addition of new scraping platforms.

## Current Status: Experimental

This project is currently **experimental**. While the scrapers are designed to be resilient, they rely on parsing third-party websites and are subject to breaking without notice if the source HTML structure changes. The underlying libraries may also be blocked by the target platforms.

**Use in a production environment is not recommended without active monitoring and maintenance.**

## Architecture Overview

The scraping architecture is designed to be robust and easy to maintain. It consists of the following components:

- **BaseScraper:** An abstract base class that defines the interface for all scrapers. Each scraper must implement the `parse` method.
- **Scraper Implementations:** Each platform (e.g., Google Search, Facebook) has its own scraper class that inherits from `BaseScraper`.
- **ScraperRegistry:** A registry that automatically discovers and registers all scraper classes. This allows for easy addition of new scrapers without modifying the core logic.
- **ScrapeOrchestrator:** A central orchestrator that receives a platform and HTML content, selects the appropriate scraper from the registry, and executes it.
- **Custom Errors:** A set of custom exception classes for handling scraper-specific errors, such as changes in HTML structure or no results being found.

## Folder Structure

The project is organized as follows:

```
├── backend/
│   ├── api/
│   │   └── scraper.py
│   ├── services/
│   │   └── scraper.py
│   └── schemas/
│       └── scraper.py
├── scrapers/
│   ├── base.py
│   ├── registry.py
│   ├── google_search.py
│   └── ... (other scrapers)
├── tests/
│   ├── test_scrapers.py
│   └── samples/
│       └── ... (test HTML files)
├── orchestrator.py
├── errors.py
└── README.md
```

## How Scrapers are Registered

Scrapers are automatically registered with the `ScraperRegistry` using a class decorator. To register a new scraper, simply add the `@register_scraper` decorator to your scraper class:

```python
from scrapers.registry import register_scraper

@register_scraper
class MyNewScraper(BaseScraper):
    platform = "my_new_platform"
    ...
```

## How to Add a New Platform

Adding a new platform is a straightforward process:

1.  **Create a new scraper file:** Create a new Python file in the `scrapers/` directory (e.g., `scrapers/my_new_platform.py`).
2.  **Implement the scraper class:** In the new file, create a new class that inherits from `BaseScraper` and implements the `parse` method.
3.  **Set the platform attribute:** Set the `platform` class attribute to a unique identifier for the new platform.
4.  **Register the scraper:** Add the `@register_scraper` decorator to the new scraper class.
5.  **Import the scraper:** Import the new scraper module in `scrapers/__init__.py` to ensure it's registered when the application starts.
6.  **Add tests:** Create a new test file in the `tests/` directory with unit tests for the new scraper.

## How to Update a Scraper when HTML Changes

When the HTML structure of a platform changes, the corresponding scraper may need to be updated. Here's the recommended workflow:

1.  **Identify the failed scraper:** The application will return a structured error message indicating which platform failed and why.
2.  **Obtain the new HTML:** Get a sample of the new HTML that is causing the scraper to fail.
3.  **Update the scraper logic:** Modify the `parse` method of the scraper to correctly extract the data from the new HTML structure.
4.  **Update the tests:** Update the test cases in the `tests/` directory to reflect the changes in the HTML and the scraper.
5.  **Run the tests:** Run the tests to ensure that the updated scraper is working correctly and that no existing functionality has been broken.

## How Errors are Surfaced

Scraper-specific errors are handled gracefully and returned to the API caller as a structured JSON object. This allows the frontend to display a user-friendly error message and provides developers with the information they need to debug the issue.

Example of an error response:

```json
{
  "status": "error",
  "platform": "google_search",
  "reason": "No results found in HTML",
  "failed_fields": [],
  "recommended_action": "Verify the input HTML contains business listings."
}
```

## Best Practices for Resilient Parsing

To ensure that the scrapers are resilient to changes in the HTML, follow these best practices:

-   **Use structural and semantic selectors:** Instead of relying on brittle CSS classes, use selectors that are based on the structure of the document (e.g., `div > h1`) or semantic attributes (e.g., `[aria-label="business-name"]`).
-   **Handle missing data gracefully:** Don't assume that all fields will be present for every business. Use `try...except` blocks or check for the existence of elements before trying to access their content.
-   **Use fallback strategies:** If there are multiple ways to extract a piece of data, implement fallback strategies to try different selectors if the primary one fails.
-   **Write comprehensive tests:** Write tests that cover a variety of scenarios, including missing data, different HTML structures, and error conditions.
