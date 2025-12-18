from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Lead:
    """Data model for a lead."""
    name: str
    company: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    source: Optional[str] = None
    linkedin_profile: Optional[str] = None
    notes: Optional[str] = None
    timestamp: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())
