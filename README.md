# AI-Powered Lead Discovery & Scraper Agent

This project is an AI-powered agent for discovering and scraping leads from various sources. It is designed to be easily extensible for adding new data sources.

## Architecture Overview

The agent is designed with a modular architecture to separate concerns and allow for easy extensibility.

- **`main.py`**: The entry point of the application. It orchestrates the lead discovery and scraping process.
- **`config.py`**: Contains configuration settings for the agent, such as API keys and data source configurations.
- **`src/agent/models/lead.py`**: Defines the data model for a "Lead".
- **`src/agent/sources/`**: This package contains modules for different lead sources. Each source module is responsible for scraping data from a specific source.
    - **`base_source.py`**: Defines the abstract base class for all data sources, ensuring a consistent interface.
- **`src/agent/storage/excel_storage.py`**: Handles saving the scraped lead data to an Excel file.

## Execution Flow

1. **Initialization**: The `main.py` script is executed. It loads the configuration from `config.py`.
2. **Source Selection**: The agent selects the data sources to scrape from (this will be configured in `config.py`).
3. **Scraping**: For each selected source, the agent calls the `scrape` method of the corresponding source module.
4. **Data Storage**: The scraped data, in the form of `Lead` objects, is passed to the `ExcelStorage` module.
5. **Saving**: The `ExcelStorage` module saves the lead data to an Excel file in the `data/` directory.

## How to Add a New Source

1. Create a new file in `src/agent/sources/` (e.g., `new_source.py`).
2. In this new file, create a class that inherits from `BaseSource` (defined in `base_source.py`).
3. Implement the `scrape` method in your new class. This method should contain the logic for scraping leads from the new source.
4. Update the configuration in `config.py` to include your new source.
