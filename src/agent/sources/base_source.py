from abc import ABC, abstractmethod
from typing import List
from src.agent.models.lead import Lead

class BaseSource(ABC):
    """Abstract base class for a lead data source."""

    @abstractmethod
    def scrape(self) -> List[Lead]:
        """
        Scrapes leads from the source.

        This method should be implemented by each subclass. It is responsible
        for the entire process of fetching and parsing data from the source,
        and returning it as a list of Lead objects.

        Returns:
            A list of Lead objects.
        """
        pass
