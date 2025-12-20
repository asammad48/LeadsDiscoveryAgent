# Lead Discovery & Scraper Agent

This project is a web application that allows users to discover and scrape leads from various sources.

## Local Run Instructions

To run the application locally, you will need to have Python, Node.js, and npm installed.

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    cd frontend
    npm install
    ```

2.  **Start the backend server:**
    ```bash
    export PYTHONPATH=$PYTHONPATH:$(pwd)
    uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ```

3.  **Start the frontend server:**
    ```bash
    cd frontend
    npm start
    ```

The application will be available at http://localhost:3000.

## CORS Verification

CORS is configured in `backend/main.py` to allow requests from `http://localhost:3000`. This can be verified by running the application and making a request from the frontend to the backend.

## Test Cases

The following test cases can be used to verify the functionality of the application:

1.  **Query:** "Top 5G companies in China"
    **Expected result:** The results table should populate with data related to 5G companies in China, and the "Download as Excel" button should become active.
2.  **Query:** "Leading AI research labs in Europe"
    **Expected result:** The results table should display a list of AI research labs in Europe, and the download button should be enabled.
3.  **Query:** "Best coffee shops in my neighborhood"
    **Expected result:** The results table should show a list of nearby coffee shops, and the download button should be enabled.
