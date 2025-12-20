from pydantic import BaseModel
from typing import Optional, Dict, List

class ScraperRequest(BaseModel):
    query: str

# Defines the structure for a single, authoritative business entity
class BusinessLead(BaseModel):
    business_name: str
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    sources: Dict[str, str]

# The main API response is now a list of these authoritative leads,
# alongside the original query and any errors.
class ScraperResponse(BaseModel):
    query: str
    platforms: List[BusinessLead] # Renamed to 'platforms' for consistency, but holds the final list
    errors: list
    filename: Optional[str] = None # No longer used, but kept for compatibility
    pagination: Dict[str, bool] # Kept for potential future use
