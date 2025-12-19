"""
This module provides function to scrape Google search results safely and effectively.

It includes explanations and implementations for:
- Google search operators
- Query patterns for business discovery
- Site targeting (e.g., site:linkedin.com)
- Title & snippet parsing
- Pagination handling
- Rate limiting and safe scraping practices

**Google Search Operators:**

Google search operators are special keywords and symbols that extend the capabilities of
regular text searches. Below are some of the most useful operators for business discovery:

- `site:`: Restricts the search to a specific website.
  (e.g., `site:linkedin.com "software engineers in London"`)
- `inurl:`: Finds pages with a specific keyword in the URL.
- `intitle:`: Finds pages with a specific keyword in the title.
- `intext:`: Finds pages with a specific keyword in the body of the text.
- `""`: (Quotes) Searches for an exact phrase.
- `*`: (Asterisk) Acts as a wildcard for any word or phrase.
- `-`: (Minus sign) Excludes a specific keyword from the search results.
- `OR`: Searches for pages that contain either of two keywords.
- `AND`: Searches for pages that contain both keywords.
- `related:`: Finds websites related to a specific domain.

**Query Patterns for Business Discovery:**

Effective business discovery relies on crafting targeted queries. Here are some patterns:

- **Industry + Location + "contact"**: ` "plumbers in san diego" "contact" `
- **"top * companies in [industry]"**: `"top 10 software companies in california"`
- **site:linkedin.com "[job title]" "[location]"**:
`site:linkedin.com "data scientist" "new york"`

**Site Targeting:**

To focus on specific platforms, use the `site:` operator. For example, to find potential
leads on LinkedIn, you would use `site:linkedin.com`. This is highly effective for
sourcing professionals or companies from a particular domain.

**Title & Snippet Parsing:**

After fetching the HTML of the search results, the next step is to parse it to extract
the relevant information. This typically involves:
- Identifying the HTML tags that contain the search result titles, URLs, and snippets.
- Using a library like BeautifulSoup to select these tags and extract their content.

**Pagination Handling:**

Google search results are paginated. To get a comprehensive list of results, a scraper
must be able to navigate through these pages. This is usually done by:
- Identifying the "Next" button or the page number links in the HTML.
- Modifying the search URL to request the next page of results.
- Looping until there are no more pages or a desired number of pages has been scraped.

**Rate Limiting and Safe Scraping:**

To avoid being blocked by Google, it's crucial to scrape responsibly. Key practices include:
- **User-Agent Rotation**:
  - The User-Agent is an HTTP header that identifies the client (e.g., browser) to the server.
  - Sending requests with a variety of common User-Agent strings makes the scraper appear
    more like a human user and less like a bot.
- **Adding Delays**:
  - Making requests too quickly can trigger anti-scraping mechanisms.
  - Introducing random delays between requests mimics human browsing behavior and reduces the
    load on the server.
- **Using Proxies**:
  - For large-scale scraping, rotating IP addresses using proxies is essential to avoid IP-based
    blocking.
"""

import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_google(query, num_pages=1):
    """
    Scrapes Google search results for a given query.

    Args:
        query (str): The search query.
        num_pages (int): The number of pages to scrape.

    Returns:
        list: A list of dictionaries, where each dictionary represents a search result
              and contains the title, URL, and snippet.
    """
    results = []
    for page in range(num_pages):
        start = page * 10
        url = f"https://www.google.com/search?q={query}&start={start}"

        # Rotate user agents to avoid being blocked
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
        ]
        headers = {'User-Agent': random.choice(user_agents)}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes

            soup = BeautifulSoup(response.text, 'html.parser')

            # Google's search result structure can change, so these selectors may need updating.
            # The 'g' class is a common container for each search result.
            for g in soup.find_all('div', class_='g'):
                # The 'yuRUbf' class typically contains the link and title
                rc = g.find('div', class_='yuRUbf')
                if rc:
                    link_tag = rc.find('a')
                    title_tag = rc.find('h3')

                    if link_tag and title_tag:
                        url = link_tag['href']
                        title = title_tag.get_text()

                        # The 'VwiC3b' class often holds the snippet
                        snippet_tag = g.find('div', class_='VwiC3b')
                        snippet = snippet_tag.get_text() if snippet_tag else ""

                        results.append({'title': title, 'url': url, 'snippet': snippet})

            # Add a random delay to mimic human behavior and avoid rate limiting
            time.sleep(random.uniform(1, 3))

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break

    return results

if __name__ == "__main__":
    # Example queries for business discovery
    queries = [
        'site:linkedin.com "software engineer" "san francisco"',
        '"top real estate agencies in new york" contact',
        'intext:"we are hiring" "data scientists"'
    ]

    for query in queries:
        print(f"--- Scraping results for: '{query}' ---")
        scraped_results = scrape_google(query, num_pages=1)
        for i, result in enumerate(scraped_results, 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['url']}")
            print(f"   {result['snippet']}")
        print("-" * 30)
