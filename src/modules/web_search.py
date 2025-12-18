from ddgs import DDGS

def search_web(query: str, num_results: int = 10):
    """
    Performs a web search using DuckDuckGo and returns a list of URLs.

    :param query: The search query.
    :param num_results: The number of results to return.
    :return: A list of URLs.
    """
    with DDGS() as ddgs:
        results = [r['href'] for r in ddgs.text(query, max_results=num_results)]
        return results

if __name__ == '__main__':
    results = search_web("Python developers in San Francisco")
    if results:
        for result in results:
            print(result)
    else:
        print("No results found.")
