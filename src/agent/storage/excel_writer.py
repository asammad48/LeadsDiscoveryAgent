import os
from typing import List
import pandas as pd
from dataclasses import asdict
from src.agent.models.lead import Lead

class ExcelWriter:
    """Handles saving lead data to an Excel file in append mode, avoiding duplicates."""

    def __init__(self, filename: str = "leads.xlsx"):
        """
        Initializes the ExcelWriter.

        Args:
            filename: The name of the Excel file to write to.
        """
        self.filename = filename

    def save(self, leads: List[Lead]):
        """
        Saves a list of leads to the Excel file.

        If the file already exists, it appends the new leads, avoiding duplicates.
        Duplicates are identified by 'website' if present, otherwise by the
        combination of 'company' and 'city'.

        Args:
            leads: A list of Lead objects to save.
        """
        if not leads:
            return

        new_leads_df = pd.DataFrame([asdict(lead) for lead in leads])

        try:
            existing_leads_df = pd.read_excel(self.filename)
            combined_df = pd.concat([existing_leads_df, new_leads_df], ignore_index=True)
        except FileNotFoundError:
            combined_df = new_leads_df

        # Define a priority-based key for deduplication
        # Use website if it's not null, otherwise use company_city
        combined_df['dedupe_key'] = combined_df['website'].fillna(combined_df['company'].fillna('') + '_' + combined_df['city'].fillna(''))

        # Drop duplicates, keeping the last entry (newest one if any)
        combined_df.drop_duplicates(subset=['dedupe_key'], keep='last', inplace=True)

        # Drop the temporary key column
        combined_df.drop(columns=['dedupe_key'], inplace=True)

        # Write the data to Excel
        combined_df.to_excel(self.filename, index=False, engine='openpyxl')
