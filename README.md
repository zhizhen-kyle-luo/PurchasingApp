# Purchasing App

This is a web application for managing purchases, built with an Angular frontend and a Python/Flask backend. 

There are 4 types of account, requester, sublead, executive, and business. A requester account has the ability to create an order, which will be sent to sublead for approval; once approved, it will be sent to executive for approval; once approved, it will be sent to business where they will manually track the status of order (Not Purchased -> Purchased -> Shipped -> Delivered) and update it accordingly. Once an order has been marked as Delivered, the original acount that request this order will see an Received button that replaces the delete button that basically does the same thing as the delete button. In the 3 total status transition carried out by business, they will be able to add an optional note. For the last transition to delievered, they can also upload optional image that supports JPEG, PNG, and HEIC. For sublead, its own will only need to be approved by executive and executive needs no approval. Business account needs no approval. 

For each order, there will be a button to delete it, which archives in in the all past orders page. There, you can restore the item. Restoring item willl restore this item to the status the order was at before delete button was clicked. The status flow of an order goes from Not Approved, Approved, Not Purchased, Purchased, Shipped, Delivered, and Received. These status are mutually exclusive.

For development, no email is actually being sent. For production, you will be notified whenver you needs to approve an order or equivalently, for business account only, any order has becomed fully approved and so is under not purchased status. You will also be notified if your order has been approved for every approval you need (so requester will get 2 until fully approved, sublead gets 1, business and executive will get 0 because they don't need approval) as well as when your order has been delivered. 

My current order shows all order created by you; for business acounts, here will also show all orders having status Not Purchased, Purchased, Shipped, Delivered, as these are what orders they have to work on. All current order shows all active orders made by anyone. All past orders shows all deleted or has been marked as received. The default order in which orders are shown in these 3 pages are the most recent comes first, but they should all be able to filter by vendor, requester name (who created the order), date of creation, status, urgency, subteam, sub-project. Note in my current order for non-business accounts, they should not be able to filter by requester name because my current order will show order created by me only. Business account will have this as a filter option because they will see all orders having status Not Purchased, Purchased, Shipped, Delivered. Note these filter options are not mutually exclusive and you can filtered using multiple options.

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
