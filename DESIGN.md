# System Architecture Design

## 1. Backend + Frontend Folder Structure

### Backend (FastAPI)

The backend code will be housed within the existing `src/` directory, with API-specific components organized as follows:

```
src/
├── api/
│   ├── endpoints/         # API endpoint routers (e.g., /run, /status, /download)
│   │   ├── __init__.py
│   │   └── query.py
│   ├── tasks/             # Asynchronous task management for scrapers
│   │   ├── __init__.py
│   │   └── scraper_tasks.py
│   ├── models/            # Pydantic models for API requests/responses
│   │   ├── __init__.py
│   │   └── leads.py
│   ├── __init__.py
│   └── main.py            # Main FastAPI application instance and setup
│
├── agent/                 # Core lead generation logic (remains untouched)
│   ├── models/
│   ├── sources/
│   └── storage/
│
└── modules/               # Supporting modules (remains untouched)
```

### Frontend (React)

The frontend code will be located in the `frontend/` directory, following a standard `create-react-app` structure with a component-based organization:

```
frontend/
├── public/                # Static assets
│   └── index.html
│
└── src/
    ├── api/               # API client for backend communication
    │   └── apiClient.js
    ├── components/        # Reusable UI components
    │   ├── QueryForm.js
    │   ├── TaskStatus.js
    │   └── ResultsDisplay.js
    ├── pages/             # Main page components
    │   └── HomePage.js
    ├── App.js             # Main application component and routing
    ├── index.js           # Application entry point
    └── setupProxy.js      # Proxy configuration for API requests
```

## 2. API Boundaries

The API will expose the following endpoints to manage the lead generation process:

### **POST /api/run**

-   **Description**: Initiates a new lead generation task.
-   **Request Body**:
    ```json
    {
      "query": "string"
    }
    ```
-   **Response Body**:
    ```json
    {
      "task_id": "string"
    }
    ```

### **GET /api/status/{task_id}**

-   **Description**: Checks the status of a lead generation task.
-   **Response Body**:
    ```json
    {
      "status": "string", // e.g., "PENDING", "RUNNING", "SUCCESS", "FAILURE"
      "progress": "float", // A value between 0.0 and 1.0
      "message": "string"  // A descriptive message of the current status
    }
    ```

### **GET /api/download/{task_id}**

-   **Description**: Downloads the results of a completed task as an Excel file.
-   **Response**: The generated Excel file.

## 3. Data Flow Diagram

The following diagram illustrates the flow of data from the user's initial query to the final download of the generated leads:

```
[User] -> [React Frontend] -> [FastAPI Backend] -> [Task Queue] -> [Scraper Agent] -> [Excel File]
  |              |                  |                  |                |                  |
  1. Enter Query |                  |                  |                |                  |
  |------------> | 2. POST /api/run |                  |                |                  |
  |              |----------------> | 3. Start Task    |                |                  |
  |              |                  |----------------> | 4. Run Scrapers|                  |
  |              |                  |                  |--------------> | 5. Save Results  |
  |              |                  |                  |                |----------------> |
  |              | 6. Poll Status   |                  |                |                  |
  |              | <----------------| GET /api/status  |                |                  |
  |              |                  | <----------------|                |                  |
  | 7. Display   |                  |                  |                |                  |
  |    Download  |                  |                  |                |                  |
  | <------------|                  |                  |                |                  |
  |              |                  |                  |                |                  |
  8. Click       |                  |                  |                |                  |
  |    Download  |                  |                  |                |                  |
  |------------> | 9. GET /download |                  |                |                  |
  |              |----------------> | 10. Serve File   |                |                  |
  |              |                  | <---------------------------------------------------|
  | <-------------------------------|                  |                |                  |
  |  (Excel File)                   |                  |                |                  |
```

## 4. How Scraper is Called Safely

To ensure the safe and non-blocking execution of scrapers, the system will use a task queue to run them in the background. This approach decouples the long-running scraper jobs from the web server, preventing timeouts and keeping the API responsive.

### 1. Asynchronous Task Execution

-   **Task Queue**: We will use **Celery** with **Redis** as the message broker. When the `/api/run` endpoint is called, it will not execute the scraper directly. Instead, it will dispatch a new job to the Celery task queue.
-   **Immediate Response**: The API will immediately return a unique `task_id` to the client, allowing the frontend to track the job's progress without waiting for it to complete.

### 2. State Management

-   **Task State**: Celery automatically tracks the state of each task (e.g., `PENDING`, `STARTED`, `SUCCESS`, `FAILURE`). The `/api/status/{task_id}` endpoint will query Celery's backend (Redis) to get the latest status of the task.
-   **Custom Progress**: For more granular progress tracking, the scraper agent will be modified to update the task's state periodically with custom metadata, such as the percentage of sources scraped.

### 3. Safe and Isolated Execution

-   **Error Handling**: Each scraper will be executed within a `try...except` block inside the Celery task. If a scraper fails, the exception will be caught, the task's status will be set to `FAILURE`, and the error message will be saved. This prevents a single scraper failure from crashing the entire process.
-   **Process Isolation**: Celery workers run as separate processes from the web server. This isolation ensures that resource-intensive scraping tasks do not impact the performance or stability of the API.
-   **Timeouts**: A timeout will be configured for each task to prevent scrapers from running indefinitely. If a task exceeds its time limit, it will be terminated, and its status will be marked as `FAILURE`.
