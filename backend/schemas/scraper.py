from pydantic import BaseModel
from typing import Optional

class ScraperRequest(BaseModel):
    query: str

class ScraperResponse(BaseModel):
    message: str
    filename: Optional[str] = None
