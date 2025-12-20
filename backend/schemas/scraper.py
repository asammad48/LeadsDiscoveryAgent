from pydantic import BaseModel
from typing import Optional, Dict

class ScraperRequest(BaseModel):
    query: str

class ScraperResponse(BaseModel):
    query: str
    platforms: Dict[str, list]
    pagination: Dict[str, bool]
    errors: list
    filename: Optional[str] = None
