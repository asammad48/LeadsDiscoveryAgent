import pytest
import os

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")

@pytest.fixture(scope="session")
def samples_dir():
    if not os.path.exists(SAMPLES_DIR):
        os.makedirs(SAMPLES_DIR)

    # Create a dummy google_search.html for testing
    google_search_path = os.path.join(SAMPLES_DIR, "google_search.html")
    if not os.path.exists(google_search_path):
        with open(google_search_path, "w", encoding="utf-8") as f:
            f.write("""
            <html><body>
                <div class="uMdZh">
                    <div role="heading">Test Business 1</div>
                    <div class="vwVdIc" href="/url?q=https://example.com"></div>
                    <div aria-label="Website"><a href="/url?q=https://example.com"></a></div>
                    <div>Category 1 | +1234567890</div>
                    <div class="OSrXXb">Snippet 1</div>
                </div>
                <a id="pnnext" href="/search?q=next">Next Page</a>
            </body></html>
            """)

    # Create a dummy facebook_missing_phone.html for testing
    facebook_missing_phone_path = os.path.join(SAMPLES_DIR, "facebook_missing_phone.html")
    if not os.path.exists(facebook_missing_phone_path):
        with open(facebook_missing_phone_path, "w", encoding="utf-8") as f:
            f.write("""
            <html><body>
                <h1>Test Business Facebook</h1>
            </body></html>
            """)

    return SAMPLES_DIR
