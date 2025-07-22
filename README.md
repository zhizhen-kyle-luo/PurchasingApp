# MIT Motorsports Purchasing System

Modern full-stack web application for managing purchase orders with multi-level approval workflow.

## Architecture
- **Backend**: Flask REST API with SQLAlchemy, role-based auth, email notifications
- **Frontend**: Angular 17 with Material Design, TypeScript, reactive forms
- **Database**: SQLite (dev) / PostgreSQL (prod)

## Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Edit with your settings
python run.py init-db
python run.py create-test-users
python run.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Test
```bash
python test_backend.py
```

## Features
- Multi-level approval workflow (Sublead → Executive → Business)
- Role-based permissions (Requester, Sublead, Executive, Business)
- Email notifications for approvals and status updates
- File upload for arrival photos
- Real-time dashboard with statistics
- Responsive Material Design UI
- RESTful API with proper error handling

## Test Accounts
- requester@mit.edu / password123
- sublead@mit.edu / password123  
- executive@mit.edu / password123
- business@mit.edu / password123

## Deployment
See deployment configs in `/deploy` folder for production setup.
