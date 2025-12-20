from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..schemas.scraper import ScraperRequest, ScraperResponse
from ..services.scraper import scraper_service
import os

router = APIRouter()

@router.post("/run-scraper", response_model=ScraperResponse)
async def run_scraper(request: ScraperRequest):
    try:
        results = scraper_service.run_scraper(request.query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-excel")
async def download_excel(filename: str):
    try:
        # Basic security check to prevent directory traversal
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        file_path = scraper_service.get_excel_path(filename)
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    raise HTTPException(status_code=404, detail="File not found")
