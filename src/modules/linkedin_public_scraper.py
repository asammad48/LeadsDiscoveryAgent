"""
LinkedIn Public Scraper

This module provides functions to scrape public LinkedIn data without requiring a login.
It uses Google searches with `site:linkedin.com` to find company pages and then
parses the public HTML of those pages.

Search Query Templates and Keyword Strategy:

1.  **Basic Company Search:**
    - "[Company Name] linkedin"
    - Example: "Google linkedin"

2.  **Industry + Location Search:**
    - "[Industry] in [Location] linkedin company"
    - Example: "Software development in San Francisco linkedin company"

3.  **Keyword & Hashtag Strategy:**
    - Combine keywords that businesses in a target industry might use in their descriptions.
    - Use common industry hashtags in your search query.
    - Example: "B2B SaaS #fintech #startup linkedin company"

4.  **Finding Posts and Articles for Keyword Ideas:**
    - "linkedin.com/pulse [topic]"
    - "linkedin.com/feed/hashtag/[hashtag]"
    - Use these to find what keywords and phrases are trending in an industry.

Note: The effectiveness of these searches can be limited by Google's search algorithm
and the public visibility of LinkedIn pages.
"""
import json
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS


def search_linkedin_google(query, max_results=20):
    """
    Searches Google for LinkedIn pages matching the query.

    Args:
        query (str): The search query.
        max_results (int): The maximum number of results to return.

    Returns:
        list: A list of search result dictionaries.
    """
    with DDGS() as ddgs:
        return list(ddgs.text(f"site:linkedin.com {query}", max_results=max_results))


def is_company_url(url):
    """
    Checks if a URL is a LinkedIn company page URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a company page, False otherwise.
    """
    return "/company/" in url and "/in/" not in url


def is_profile_url(url):
    """
    Checks if a URL is a LinkedIn profile page URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a profile page, False otherwise.
    """
    return "/in/" in url and "/company/" not in url


def scrape_linkedin_company_page(url):
    """
    Scrapes a LinkedIn company page for public information.

    Args:
        url (str): The URL of the LinkedIn company page.

    Returns:
        dict: A dictionary containing the scraped data, or None if scraping fails.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {}

    # Prioritize extracting data from JSON-LD script tag
    script_tag = soup.find('script', {'type': 'application/ld+json'})
    if script_tag:
        try:
            json_data = json.loads(script_tag.string)
            # Find the dictionary for the organization
            org_data = next((item for item in json_data['@graph'] if item.get('@type') == 'Organization'), None)
            if org_data:
                data['name'] = org_data.get('name')
                data['description'] = org_data.get('description')
                data['url'] = org_data.get('url')
                data['logo'] = org_data.get('logo')
                data['industry'] = org_data.get('industry')
        except (json.JSONDecodeError, KeyError, StopIteration):
            # Fallback to HTML parsing if JSON is malformed or doesn't have expected structure
            pass

    # Fallback or supplement with HTML parsing
    if not data.get('name'):
        name_tag = soup.find('h1', class_='top-card-layout__title')
        if name_tag:
            data['name'] = name_tag.get_text(strip=True)

    if not data.get('description'):
        # LinkedIn company descriptions are often in a specific section
        # The class names can change, so this might need adjustment
        description_section = soup.find('section', {'data-test-id': 'about-us__description'})
        if description_section:
            data['description'] = description_section.get_text(strip=True)

    # Industry Inference Logic
    if not data.get('industry'):
        # Fallback 1: Check for a specific div class used in the layout
        industry_tag = soup.find('div', class_='top-card-layout__seed-item')
        if industry_tag:
            data['industry'] = industry_tag.get_text(strip=True)

    if not data.get('industry'):
        # Fallback 2: Look for a definition list item with the term "Industry"
        try:
            industry_dt = soup.find('dt', string=lambda t: t and 'industry' in t.lower())
            if industry_dt:
                industry_dd = industry_dt.find_next_sibling('dd')
                if industry_dd:
                    data['industry'] = industry_dd.get_text(strip=True).strip()
        except Exception:
            pass  # Avoid crashing if the search fails

    return data
