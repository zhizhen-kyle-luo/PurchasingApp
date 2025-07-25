# MIT Motorsports Purchasing Management System

A comprehensive web application for managing purchase orders and approvals within MIT Motorsports team structure. The system implements a multi-level approval workflow with role-based access control and real-time status tracking.

## Overview

This application streamlines the purchasing process for MIT Motorsports by implementing a structured approval workflow that ensures proper oversight and tracking of all purchase orders from creation to delivery.

### Core Workflow

```
Requester → Sublead → Executive → Business
    ↓         ↓         ↓          ↓         
  Create    Approve   Approve  Track Status
```

## System Architecture

### User Roles & Permissions

| Role | Create Orders | Approve Orders | Purchase Orders | Special Rules |
|------|---------------|----------------|-----------------|---------------|
| **Requester** | Y | N | N | Standard approval flow |
| **Sublead** | Y | Y (Requester orders) | N | Own orders → Executive only |
| **Executive** | Y | Y (Requester and Sublead) | N | No approval needed |
| **Business** | Y | N | Y | No approval needed |

### Order Status Flow

An order progresses through two distinct status tracks: Approval and Purchase.

**1. Approval Status**
This track represents the approval workflow. An order must be fully approved before it can be purchased.
`Pending Sublead Approval` → `Pending Executive Approval` → `Fully Approved`

**2. Purchase Status**
Once an order is `Fully Approved`, it enters the purchasing workflow with an initial status of `Not Yet Purchased`. The Business team then updates the status as the order is fulfilled.
`Not Yet Purchased` → `Purchased` → `Shipped` → `Arrived`

## Key Features

### Implemented Features
- **Multi-level Approval Workflow**: Automated routing based on user roles
- **Role-based Dashboard Views**: Customized interfaces per user type
- **Order Management**: Create, approve, reject, delete, and restore orders
- **File Upload System**: Support for delivery photos (JPEG, PNG, HEIC)
- **Soft Delete**: Archive orders without permanent deletion
- **User Authentication**: Secure login with session management
- **Responsive UI**: Modern Angular frontend with Tailwind CSS

### Dashboard Views

#### My Current Orders
- **For Business Users**: Shows all orders requiring action (status is Not Purchased, Purchased, Shipped, or Delivered).
- **For Non-Business Users (Requesters, Subleads, Executives)**: Shows orders created by the user, **plus** any orders that are specifically awaiting that user's approval.

#### All Current Orders
- Shows all active orders from all users
- Available to all user types

#### All Past Orders
- Shows deleted orders and orders marked as received
- Supports order restoration

### Filtering System

All dashboard views support multi-criteria filtering:
- **Vendor Name**
- **Requester Name**
- **Date of Creation**
- **Order Status**
- **Urgency Level**
- **Subteam**
- **Sub-project**

*Note: Filters are non-exclusive and can be combined*

### Notification System

**Development Environment**: No emails sent

**Production Environment**:
- **Approval Requests**: Notify approvers when orders need review
- **Approval Confirmations**: Notify requesters when orders are approved
- **Status Updates**: Notify requesters when orders are delivered
- **Business Notifications**: Alert business team of fully approved orders

## Technical Stack

### Backend
- **Framework**: Flask 3.0 with SQLAlchemy ORM
- **Database**: PostgreSQL 15
- **Authentication**: Flask-Login with session management
- **File Handling**: Secure upload with validation
- **Email**: Flask-Mail (production only)

### Frontend
- **Framework**: Angular 17 with standalone components
- **Styling**: Tailwind CSS with custom SCSS
- **State Management**: RxJS with services
- **UI Components**: Custom component library
- **Authentication**: HTTP interceptors with session cookies

### Infrastructure
- **Development**: Local development servers
- **Database**: PostgreSQL with indexed queries
- **File Storage**: Local filesystem with organized structure

## Project Structure

```bash
PurchasingApp/
├── .env.example
├── .gitattributes
├── .gitignore
├── package.json
├── README.md
├── requirements.txt
├── start.py
├── backend/
│   ├── Dockerfile
│   ├── migrate.py
│   ├── requirements.txt
│   ├── run.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── purchase.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── email_service.py
│   │   │   ├── file_service.py
│   │   │   └── purchase_service.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── auth.py
│   │   │   └── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── instance/
│   │   └── mit_motorsports_purchasing.db
│   └── templates/
│       └── email/
│           └── approval_notification.html
├── frontend/
│   ├── angular.json
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.html
│       ├── main.ts
│       ├── styles.scss
│       ├── app/
│       │   ├── app.component.ts
│       │   ├── app.config.ts
│       │   ├── app.routes.ts
│       │   ├── components/
│       │   ├── guards/
│       │   ├── interceptors/
│       │   ├── models/
│       │   └── services/
│       ├── assets/
│       └── environments/
└── README.md
```

## Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **PostgreSQL 12+**

### Environment Setup

Before running the application, you need to create your own .env based on the .env.exmaple provided.

### Option 1: Automated Setup

```bash
# Clone the repository
git clone <repository-url>
cd PurchasingApp

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run the unified startup script
python start.py
```

**What this does:**
- Initializes database and creates test users
- Starts Flask backend server (`http://localhost:5000`)
- Installs frontend dependencies
- Starts Angular development server (`http://localhost:4200`)

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python migrate.py

# Start backend server
python run.py
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Test Accounts

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| Requester | `requester@mit.edu` | `password123` | Can create orders |
| Sublead | `sublead@mit.edu` | `password123` | Approves requester orders |
| Executive | `executive@mit.edu` | `password123` | Final approval authority |
| Business | `business@mit.edu` | `password123` | Handles purchasing & fulfillment |

## Requirements Verification

### Core Functionality Status

| Requirement | Status | Notes |
|-------------|--------|-------|
| **User Authentication** | Complete | Session-based auth with role management |
| **Order Creation** | Complete | Full form with validation |
| **Approval Workflow** | Complete | Multi-level approval routing |
| **Status Tracking** | Complete | Business team status updates |
| **File Upload** | Complete | Delivery photo support (JPEG, PNG, HEIC) |
| **Soft Delete/Restore** | Complete | Archive and restore functionality |
| **Dashboard Views** | Complete | My/All Current/Past orders |
| **Role-based Access** | Complete | Different permissions per role |
| **Filtering System** | Partial | Basic filters implemented, needs enhancement |
| **Email Notifications** | Partial | Framework ready, production config needed |
| **Responsive Design** | Complete | Mobile-friendly UI |

### Dashboard View Requirements

| View | Requirement | Status |
|------|-------------|--------|
| **My Current Orders** | Show user's own orders and orders awaiting their approval (non-business) | Complete |
| **My Current Orders** | Show actionable orders (business) | Complete |
| **All Current Orders** | Show all active orders | Complete |
| **All Past Orders** | Show deleted/received orders | Complete |
| **Filtering** | Multi-criteria filtering | Partial |
| **Sorting** | Most recent first | Complete |

### Approval Workflow Requirements

| Scenario | Expected Flow | Status |
|----------|---------------|--------|
| **Requester Order** | Requester → Sublead → Executive → Business | Complete |
| **Sublead Order** | Sublead → Executive → Business | Complete |
| **Executive Order** | Executive → Business | Complete |
| **Business Order** | Business (no approval) | Complete |

### Status Flow Requirements

| Transition | Trigger | Status |
|------------|---------|--------|
| **Not Approved → Approved** | Approval completion | Complete |
| **Approved → Not Purchased** | Business receives | Complete |
| **Not Purchased → Purchased** | Business marks bought | Complete |
| **Purchased → Shipped** | Business marks shipped | Complete |
| **Shipped → Delivered** | Business marks delivered | Complete |
| **Delivered → Received** | Requester confirms | Complete |

## Development

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/purchases` | GET | List purchases with filters |
| `/api/purchases` | POST | Create new purchase |
| `/api/purchases/<id>` | GET | Get purchase details |
| `/api/purchases/<id>/approve` | POST | Approve purchase |
| `/api/purchases/<id>/reject` | POST | Reject purchase |
| `/api/purchases/<id>/status` | PUT | Update purchase status |
| `/api/purchases/<id>/delete` | DELETE | Soft delete purchase |
| `/api/purchases/<id>/restore` | POST | Restore deleted purchase |

## Known Issues & TODO

### High Priority
- [ ] Implement comprehensive filtering system
- [ ] Complete email notification setup for production
- [ ] Add input validation for all forms
- [ ] Implement proper error handling

### Medium Priority
- [ ] Add bulk operations for orders
- [ ] Implement order search functionality
- [ ] Add export functionality (CSV/PDF)
- [ ] Performance optimization for large datasets

### Low Priority
- [ ] Add dark mode support
- [ ] Implement real-time notifications
- [ ] Add audit trail for all actions
- [ ] Mobile app development

## Support

For issues and questions:
1. Check existing GitHub issues
2. Create new issue with detailed description
3. Contact development team

## License

This project is proprietary software developed for MIT Motorsports team.
