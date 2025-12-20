# Local Development and Realtime Usage Guide

This guide provides a complete overview of how to set up, run, and use the Lead Discovery & Scraper Agent for local development and testing.

---

## 1. SYSTEM PREREQUISITES

Ensure your development environment meets the following requirements:

-   **Python**: `3.9+`
-   **Node.js**: `14.x+`
-   **npm**: `6.x+` (comes with Node.js)
-   **Operating System**: The application is compatible with macOS, Linux, and Windows.

---

## 2. PROJECT STRUCTURE OVERVIEW

The project is organized into two main parts: a FastAPI backend and a React frontend.

-   **`backend/`**: Contains the Python-based FastAPI application.
    -   **`api/`**: Defines the API endpoints (`/run-scraper`, `/download-excel`).
    -   **`services/`**: Includes the core business logic for the scraper.
    -   **`main.py`**: The entry point for the FastAPI application, where CORS and routing are configured.
-   **`frontend/`**: Contains the React-based user interface.
    -   **`src/components/`**: Reusable React components for the UI.
    -   **`src/services/`**: Handles communication with the backend API.
    -   **`App.js`**: The main application component that manages the UI state.
-   **`output/`**: This directory is automatically created when the scraper runs and is where the generated Excel file is stored.

---

## 3. BACKEND (FASTAPI) — DEVELOPMENT MODE

Follow these steps to get the backend server running with hot reload for development.

1.  **Create a Virtual Environment**:
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    venv\Scripts\activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set the PYTHONPATH**:
    ```bash
    # For macOS/Linux
    export PYTHONPATH=$PYTHONPATH:$(pwd)

    # For Windows (in Command Prompt)
    set PYTHONPATH=%PYTHONPATH%;%cd%
    ```

4.  **Run the Backend with Hot Reload**:
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
    ```

5.  **Expected Startup Logs**:
    ```
    INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [12345]
    INFO:     Started server process [12347]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

6.  **Verify Backend is Working**:
    -   Open your browser and navigate to [http://localhost:8000/docs](http://localhost:8000/docs). You should see the FastAPI Swagger UI with the available endpoints.

---

## 4. FRONTEND (REACT) — DEVELOPMENT MODE

Here’s how to set up and run the frontend development server.

1.  **Install Frontend Dependencies**:
    ```bash
    cd frontend
    npm install
    ```

2.  **Run the Dev Server**:
    ```bash
    npm start
    ```

3.  **Expected URL**:
    -   The frontend will be available at [http://localhost:3000](http://localhost:3000).

4.  **How Frontend Connects to Backend**:
    -   The frontend uses a proxy to forward API requests to the backend. This is configured in `frontend/package.json` with the `"proxy": "http://localhost:8000"` setting, which prevents CORS issues during development.

---

## 5. REALTIME USAGE FLOW

This is how the application works in realtime:

1.  **User Enters Query**: The user types a query into the search box and clicks "Run Scraper."
2.  **API Request**: The frontend sends a `POST` request to the `/api/run-scraper` endpoint.
3.  **Scraper Execution**: The backend executes the scraper in realtime, blocking the request until the scraping is complete.
4.  **Results Display**: The results are returned to the frontend and displayed in the results table.
5.  **Excel File Creation**: The Excel file is created in the `output/` directory.
6.  **Download**: The "Download as Excel" button becomes active, and the user can download the generated file.

---

## 6. COMMON ISSUES & FIXES

-   **UI Not Rendering**:
    -   **Fix**: Ensure you have run `npm install` in the `frontend` directory and that there are no errors in the browser's developer console.
-   **CORS Errors**:
    -   **Fix**: The proxy should handle this, but if you encounter CORS issues, verify that the `"proxy"` setting in `frontend/package.json` is correct and that the backend server is running.
-   **API Not Reachable / Port Conflicts**:
    -   **Symptom**: The application fails to start with an error like `Address already in use`.
    -   **Fix**: This means another process is using port `8000` or `3000`.
        -   **For the backend**, you can run it on a different port by using the `--port` flag:
            ```bash
            uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
            ```
            If you change the backend port, remember to update the `"proxy"` setting in `frontend/package.json` to match the new port.
        -   **For the frontend**, the React development server will automatically prompt you to use a different port if `3000` is unavailable. Simply press `y` when asked.
-   **Excel Not Downloading**:
    -   **Fix**: Check the `output/` directory to see if the file was created. If not, check the backend logs for errors.
-   **Scraper Slow / Blocking UI**:
    -   **Fix**: This is expected since the scraper runs synchronously. For long-running scrapers, this will be improved in a future update with background processing.

---

## 7. DEVELOPMENT BEST PRACTICES

-   **Rate Limiting**: Be mindful of rate limiting when scraping websites to avoid being blocked.
-   **Running Scrapers Selectively**: For development, you can modify the scraper service to run only specific scrapers to speed up testing.
-   **Debug Logging**: Add `print()` statements or use a logging library in the backend to debug the scraper's execution.
-   **Safe Scraping**: Always respect the terms of service of the websites you are scraping and avoid scraping personal data.
