from pydantic import BaseModel
from typing import Optional, Dict, List

class ScraperRequest(BaseModel):
    query: str

class BusinessLead(BaseModel):
    business_name: str
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    sources: Dict[str, str]

class ScraperResponse(BaseModel):
    query: str
    platforms: List[BusinessLead]
    errors: list
    filename: Optional[str] = None
    pagination: Dict[str, bool]
