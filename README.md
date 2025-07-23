# Purchasing App

This is a web application for managing purchases, built with an Angular frontend and a Python/Flask backend.

## Tech Stack

- **Frontend:** Angular
- **Backend:** Flask (Python)
- **Database:** PostgreSQL


## Project Structure

- `backend/`: Contains the structured Flask backend application. This is the primary backend for the project.
- `frontend/`: Contains the Angular frontend application.
- `app.py`: A single-file Flask application.
- `start.py`: A unified startup script that automates the setup and execution of both the backend and frontend.

## Recommended: Using the Startup Script

The easiest way to get the application running is to use the `start.py` script. This will handle all the necessary setup steps for you.

1.  **Install dependencies:**
    -   Make sure you have Python 3.8+ and Node.js 16+ installed.
    -   Install the required Python packages:
        ```bash
        pip install -r backend/requirements.txt
        ```

2.  **Run the startup script:**
    ```bash
    python start.py
    ```

This will:
-   Initialize the database and create test users if the database does not exist.
-   Start the backend server.
-   Install frontend dependencies if they are missing.
-   Start the frontend server.

The application will be available at `http://localhost:4200/`.

**Important:**
- If the database file (`backend/instance/purchases_dev.db`) already exists, `start.py` will NOT re-initialize the database or create test users. If you need to reset the database (for example, if test users are missing or you encounter login errors), you should delete the `backend/instance/purchases_dev.db` file and re-run `python start.py`, or manually run the migration script:
    ```bash
    cd backend
    ../venv/Scripts/python.exe migrate.py
    ```

## Manual Setup

If you prefer to set up the backend and frontend manually, follow these steps.

### Backend Setup

You will need one terminal for the backend.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    -   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    -   On macOS/Linux:
        ```bash
        python -m venv venv
        source venv/bin/activate
        ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database and create test users:**
    This only needs to be done once, unless you want to reset the database.
    ```bash
    python migrate.py
    ```

5.  **Run the backend server:**
    ```bash
    python run.py
    ```

The backend server will be running at `http://127.0.0.1:5000`.

### Frontend Setup

You will need a second terminal for the frontend.

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install npm dependencies:**
    ```bash
    npm install
    ```

3.  **Run the frontend development server:**
    ```bash
    npm start
    ```

The frontend development server will be running at `http://localhost:4200/`.

## Test Accounts

The following test accounts are available (created automatically if the database is initialized from scratch):

-   **Email:** `requester@mit.edu` / **Password:** `password123`
-   **Email:** `sublead@mit.edu` / **Password:** `password123`
-   **Email:** `executive@mit.edu` / **Password:** `password123`
-   **Email:** `business@mit.edu` / **Password:** `password123`
