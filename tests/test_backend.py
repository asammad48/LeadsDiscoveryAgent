import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import sys

# Add the backend to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_run_scraper(client):
    with patch('backend.services.scraper.scraper_service.run_scraper') as mock_run_scraper:
        mock_run_scraper.return_value = ([], "test.xlsx")
        response = client.post("/api/run-scraper", json={"query": "test query"})
        assert response.status_code == 200
        assert response.json() == {"message": "Scraping completed successfully", "filename": "test.xlsx", "results": []}
        mock_run_scraper.assert_called_once_with("test query")

def test_download_excel_file_found(client):
    # Create a dummy file for testing
    dummy_file_path = "output/dummy.xlsx"
    os.makedirs(os.path.dirname(dummy_file_path), exist_ok=True)
    with open(dummy_file_path, "w") as f:
        f.write("test data")

    with patch('backend.services.scraper.scraper_service.get_excel_path') as mock_get_excel_path:
        mock_get_excel_path.return_value = dummy_file_path
        response = client.get("/api/download-excel?filename=dummy.xlsx")
        assert response.status_code == 200
        assert response.headers['content-disposition'] == 'attachment; filename="dummy.xlsx"'
        mock_get_excel_path.assert_called_once_with("dummy.xlsx")

    # Clean up the dummy file
    os.remove(dummy_file_path)


def test_download_excel_file_not_found(client):
    with patch('backend.services.scraper.scraper_service.get_excel_path') as mock_get_excel_path:
        mock_get_excel_path.return_value = "output/nonexistent.xlsx"
        response = client.get("/api/download-excel?filename=nonexistent.xlsx")
        assert response.status_code == 404
        assert response.json() == {"detail": "File not found"}
        mock_get_excel_path.assert_called_once_with("nonexistent.xlsx")
