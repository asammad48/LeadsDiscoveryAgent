import sys
import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any

# Add src to python path to allow for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agent.main import discover_scrapers
from src.api.scraper_service import run_scrapers_service
from src.agent.config import EXCEL_FILENAME

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# --- Pydantic Models ---
class RunRequest(BaseModel):
    query: str
    selected_scrapers: List[str]
    confidence_threshold: float = 0.0

# --- Exception Handler ---
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handles any unhandled exceptions in the application and returns a
    standardized 500 JSON error response.
    """
    logging.error(f"Unhandled exception for request {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal server error occurred.",
            "error_details": str(exc)
        },
    )

# --- API Endpoints ---
@app.get("/")
def read_root():
    """Root endpoint for basic API health check."""
    return {"message": "Lead Discovery & Scraper Agent API"}

@app.get("/api/scrapers", response_model=List[str])
def get_scrapers():
    """Returns a list of available scraper names."""
    try:
        scraper_classes = discover_scrapers()
        return [scraper.__name__ for scraper in scraper_classes]
    except Exception as e:
        logging.error(f"Failed to discover scrapers: {e}")
        # Re-raise to be caught by the generic exception handler
        raise e

@app.post("/api/run")
def run_scraper_endpoint(request: RunRequest) -> JSONResponse:
    """
    Runs the lead generation process via the scraper service and returns the results.
    """
    response_data = run_scrapers_service(
        query=request.query,
        selected_scrapers=request.selected_scrapers,
        confidence_threshold=request.confidence_threshold
    )

    status_code = 500 if response_data.get("status") == "error" else 200

    return JSONResponse(content=response_data, status_code=status_code)

@app.get("/api/download")
def download_excel():
    """
    Serves the generated Excel file for download.
    Provides a safe way to download, checking for file existence.
    """
    if not os.path.exists(EXCEL_FILENAME):
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "File not found. Please run a scraper job first."}
        )

    return FileResponse(
        path=EXCEL_FILENAME,
        filename=EXCEL_FILENAME,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
