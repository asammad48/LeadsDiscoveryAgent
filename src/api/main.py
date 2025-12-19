import sys
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from dataclasses import asdict

# Add src to python path to allow for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agent.main import discover_scrapers, generate_leads
from src.agent.storage.excel_writer import ExcelWriter

app = FastAPI()

class RunRequest(BaseModel):
    query: str
    selected_scrapers: List[str]
    confidence_threshold: float = 0.0

@app.get("/")
def read_root():
    return {"message": "Lead Discovery & Scraper Agent API"}

@app.get("/api/scrapers", response_model=List[str])
def get_scrapers():
    """Returns a list of available scraper names."""
    scraper_classes = discover_scrapers()
    return [scraper.__name__ for scraper in scraper_classes]

@app.post("/api/run")
def run_scraper(request: RunRequest) -> Dict[str, Any]:
    """Runs the lead generation process and returns the leads."""
    result = generate_leads(
        query=request.query,
        selected_scraper_names=request.selected_scrapers,
        confidence_threshold=request.confidence_threshold
    )

    leads = result["leads"]

    # Save to Excel
    excel_writer = ExcelWriter(filename="leads_output.xlsx")
    excel_writer.save(leads)

    # Convert leads to dicts for JSON response
    leads_as_dicts = [asdict(lead) for lead in leads]

    return {"leads": leads_as_dicts}

@app.get("/api/download")
def download_excel():
    """Serves the generated Excel file for download."""
    return FileResponse(path="leads_output.xlsx", filename="leads_output.xlsx", media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
