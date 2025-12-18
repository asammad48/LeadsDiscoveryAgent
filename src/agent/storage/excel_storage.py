from typing import List
from openpyxl import Workbook
from src.agent.models.lead import Lead

class ExcelStorage:
    """Handles saving lead data to an Excel file."""

    def __init__(self, filename: str):
        self.filename = filename

    def save(self, leads: List[Lead]):
        """
        Saves a list of leads to an Excel file.

        Args:
            leads: A list of Lead objects.
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Leads"

        # Write header
        header = [field.name for field in Lead.__dataclass_fields__.values()]
        ws.append(header)

        # Write data
        for lead in leads:
            row = [getattr(lead, field.name) for field in Lead.__dataclass_fields__.values()]
            ws.append(row)

        wb.save(self.filename)
