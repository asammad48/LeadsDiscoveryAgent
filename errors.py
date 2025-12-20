class ScraperError(Exception):
    """Base exception for all scraper-related errors."""
    def __init__(self, platform: str, reason: str, failed_fields: list = None, recommended_action: str = "Check scraper logic and HTML structure."):
        self.platform = platform
        self.reason = reason
        self.failed_fields = failed_fields or []
        self.recommended_action = recommended_action
        super().__init__(self.to_dict())

    def to_dict(self):
        return {
            "status": "error",
            "platform": self.platform,
            "reason": self.reason,
            "failed_fields": self.failed_fields,
            "recommended_action": self.recommended_action
        }

class HTMLStructureChangedError(ScraperError):
    """Exception raised when the HTML structure has changed."""
    def __init__(self, platform: str, failed_fields: list, recommended_action: str = "Update parser logic to match new HTML structure."):
        super().__init__(platform, "HTML structure changed", failed_fields, recommended_action)

class NoResultsFoundError(ScraperError):
    """Exception raised when no results are found in the HTML."""
    def __init__(self, platform: str, recommended_action: str = "Verify the input HTML contains business listings."):
        super().__init__(platform, "No results found in HTML", recommended_action=recommended_action)
