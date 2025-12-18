import openpyxl
import os

class ExcelStorage:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def save_to_excel(self, data: list[dict], filename: str):
        """
        Saves a list of dictionaries to an Excel file.

        :param data: A list of dictionaries, where each dictionary represents a row.
        :param filename: The name of the Excel file (e.g., "leads.xlsx").
        """
        filepath = os.path.join(self.data_dir, filename)

        workbook = openpyxl.Workbook()
        sheet = workbook.active

        if not data:
            workbook.save(filepath)
            return

        # Write headers
        headers = list(data[0].keys())
        sheet.append(headers)

        # Write data
        for row_data in data:
            row_values = [row_data.get(header, "") for header in headers]
            sheet.append(row_values)

        workbook.save(filepath)

if __name__ == '__main__':
    storage = ExcelStorage()
    sample_data = [
        {"url": "https://example.com", "source": "web_search"},
        {"url": "https://anotherexample.com", "source": "web_search"}
    ]
    storage.save_to_excel(sample_data, "test_leads.xlsx")
    print(f"Test data saved to data/test_leads.xlsx")
