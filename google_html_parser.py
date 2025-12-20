
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs

def parse_google_search_html(html: str) -> tuple[list[dict], str | None]:
    """
    Parses multiple businesses from a saved Google Search HTML page,
    extracting data from the HTML structure and the next page URL.
    """
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    seen_names = set()
    next_page_url = None

    # --- Find Next Page URL ---
    next_page_el = soup.select_one('a#pnnext')
    if next_page_el and next_page_el.has_attr('href'):
        href = next_page_el['href']
        if href.startswith('/'):
            next_page_url = "https://www.google.com" + href
        else:
            next_page_url = href

    # --- Data Extraction ---
    for container in soup.select('.uMdZh'):
        name_el = container.select_one('div[role="heading"]')
        name = name_el.get_text(strip=True) if name_el else None

        if not name or name in seen_names:
            continue

        data = {
            'name': name, 'category': None, 'address': None, 'website': None,
            'phone': None, 'snippet': None, 'source_url': None
        }

        source_link_el = container.select_one('.vwVdIc')
        if source_link_el and source_link_el.has_attr('href'):
            href = source_link_el['href']
            if href.startswith('/url?q='):
                href = parse_qs(urlparse(href).query).get('q', [None])[0]
            elif href.startswith('/'):
                href = "https://www.google.com" + href
            data['source_url'] = href

        website_container = container.find('div', attrs={'aria-label': 'Website'})
        if website_container:
            website_el = website_container.find('a', href=True)
            if website_el and website_el.has_attr('href'):
                 href = website_el['href']
                 if href.startswith('/url?q='):
                    href = parse_qs(urlparse(href).query).get('q', [None])[0]
                 data['website'] = href

        details_container = name_el.find_parent()
        if details_container:
            all_text = details_container.get_text(separator='|', strip=True)
            parts = [p.strip() for p in all_text.split('|') if p]

            for part in parts:
                if part != name and not data['category']:
                    if not re.search(r'^\d\.\d', part) and not re.search(r'\(\d+K?\)', part):
                         data['category'] = part
                if 'Carrer' in part or 'Avinguda' in part or 'Passeig' in part:
                    data['address'] = part
                if re.search(r'^\+?\d[\d\s-]{8,}$', part):
                    data['phone'] = part

        snippet_el = container.select_one('.OSrXXb')
        if snippet_el:
            data['snippet'] = snippet_el.get_text(strip=True)

        results.append(data)
        seen_names.add(name)

    return results, next_page_url
