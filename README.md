# MIT Motorsports Purchasing Management System

[![Angular](https://img.shields.io/badge/Angular-17-red)](https://angular.io/)
[![Flask](https://img.shields.io/badge/Flask-3.0-blue)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org/)

A comprehensive web application for managing purchase orders and approvals within MIT Motorsports team structure. The system implements a multi-level approval workflow with role-based access control and real-time status tracking.

## 🎯 Overview

This application streamlines the purchasing process for MIT Motorsports by implementing a structured approval workflow that ensures proper oversight and tracking of all purchase orders from creation to delivery.

### Core Workflow

```
Requester → Sublead → Executive → Business → Delivery
    ↓         ↓         ↓          ↓         ↓
  Create    Approve   Approve  Track Status
```

## 🏗️ System Architecture

### User Roles & Permissions

| Role | Create Orders | Approve Orders | Purchase Orders | Special Rules |
|------|---------------|----------------|-----------------|---------------|
| **Requester** | ✅ | ❌ | ❌ | Standard approval flow |
| **Sublead** | ✅ | ✅ (Requester orders) | ❌ | Own orders → Executive only |
| **Executive** | ✅ | ✅ (All pending) | ❌ | No approval needed |
| **Business** | ✅ | ❌ | ✅ | No approval needed |

### Order Status Flow

```
Not Approved → Approved → Not Purchased → Purchased → Shipped → Delivered → Received
```

**Status Definitions:**
- **Not Approved**: Pending sublead/executive approval
- **Approved**: Fully approved, ready for purchase
- **Not Purchased**: Approved but not yet bought
- **Purchased**: Bought by business team
- **Shipped**: In transit to destination
- **Delivered**: Arrived, pending confirmation
- **Received**: Confirmed received by requester

## 📋 Key Features

### ✅ Implemented Features
- **Multi-level Approval Workflow**: Automated routing based on user roles
- **Role-based Dashboard Views**: Customized interfaces per user type
- **Order Management**: Create, approve, reject, delete, and restore orders
- **File Upload System**: Support for delivery photos (JPEG, PNG, HEIC)
- **Soft Delete**: Archive orders without permanent deletion
- **User Authentication**: Secure login with session management
- **Responsive UI**: Modern Angular frontend with Tailwind CSS

### 🔄 Dashboard Views

#### My Current Orders
- **For Non-Business Users**: Shows orders created by the user
- **For Business Users**: Shows all orders requiring action (Not Purchased, Purchased, Shipped, Delivered)

#### All Current Orders
- Shows all active orders from all users
- Available to all user types

#### All Past Orders
- Shows deleted orders and orders marked as received
- Supports order restoration

### 🔍 Filtering System

All dashboard views support multi-criteria filtering:
- **Vendor Name**
- **Requester Name** (Business accounts only in "My Current Orders")
- **Date of Creation**
- **Order Status**
- **Urgency Level**
- **Subteam**
- **Sub-project**

*Note: Filters are non-exclusive and can be combined*

### 📧 Notification System

**Development Environment**: No emails sent (logging only)

**Production Environment**:
- **Approval Requests**: Notify approvers when orders need review
- **Approval Confirmations**: Notify requesters when orders are approved
- **Status Updates**: Notify requesters when orders are delivered
- **Business Notifications**: Alert business team of fully approved orders

## 🛠️ Technical Stack

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

## 📁 Project Structure

```bash
PurchasingApp/
├── backend/                 # Flask backend application
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic services
│   │   ├── views/          # API endpoints
│   │   └── __init__.py     # Flask app factory
│   ├── config/             # Configuration files
│   ├── requirements.txt    # Python dependencies
│   ├── migrate.py          # Database initialization
│   └── run.py             # Development server
├── frontend/               # Angular frontend application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/ # UI components
│   │   │   ├── services/   # API services
│   │   │   ├── models/     # TypeScript models
│   │   │   └── guards/     # Route guards
│   │   └── assets/         # Static assets
│   ├── package.json        # Node.js dependencies
│   └── angular.json        # Angular configuration
├── start.py               # Unified startup script
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **PostgreSQL 12+**

### Option 1: Automated Setup (Recommended)

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

## 👥 Test Accounts

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| Requester | `requester@mit.edu` | `password123` | Can create orders |
| Sublead | `sublead@mit.edu` | `password123` | Approves requester orders |
| Executive | `executive@mit.edu` | `password123` | Final approval authority |
| Business | `business@mit.edu` | `password123` | Handles purchasing & fulfillment |

## ✅ Requirements Verification

### Core Functionality Status

| Requirement | Status | Notes |
|-------------|--------|-------|
| **User Authentication** | ✅ Complete | Session-based auth with role management |
| **Order Creation** | ✅ Complete | Full form with validation |
| **Approval Workflow** | ✅ Complete | Multi-level approval routing |
| **Status Tracking** | ✅ Complete | Business team status updates |
| **File Upload** | ✅ Complete | Delivery photo support (JPEG, PNG, HEIC) |
| **Soft Delete/Restore** | ✅ Complete | Archive and restore functionality |
| **Dashboard Views** | ✅ Complete | My/All Current/Past orders |
| **Role-based Access** | ✅ Complete | Different permissions per role |
| **Filtering System** | 🔄 Partial | Basic filters implemented, needs enhancement |
| **Email Notifications** | 🔄 Partial | Framework ready, production config needed |
| **Responsive Design** | ✅ Complete | Mobile-friendly UI |

### Dashboard View Requirements

| View | Requirement | Status |
|------|-------------|--------|
| **My Current Orders** | Show user's orders (non-business) | ✅ |
| **My Current Orders** | Show actionable orders (business) | ✅ |
| **All Current Orders** | Show all active orders | ✅ |
| **All Past Orders** | Show deleted/received orders | ✅ |
| **Filtering** | Multi-criteria filtering | 🔄 |
| **Sorting** | Most recent first | ✅ |

### Approval Workflow Requirements

| Scenario | Expected Flow | Status |
|----------|---------------|--------|
| **Requester Order** | Requester → Sublead → Executive → Business | ✅ |
| **Sublead Order** | Sublead → Executive → Business | ✅ |
| **Executive Order** | Executive → Business | ✅ |
| **Business Order** | Business (no approval) | ✅ |

### Status Flow Requirements

| Transition | Trigger | Status |
|------------|---------|--------|
| **Not Approved → Approved** | Approval completion | ✅ |
| **Approved → Not Purchased** | Business receives | ✅ |
| **Not Purchased → Purchased** | Business marks bought | ✅ |
| **Purchased → Shipped** | Business marks shipped | ✅ |
| **Shipped → Delivered** | Business marks delivered | ✅ |
| **Delivered → Received** | Requester confirms | ✅ |

## 🔧 Development

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

### Environment Configuration

Create `.env` file in the root directory:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/purchasing_db

# Email (Production)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Security
SECRET_KEY=your-secret-key-here
```

## 🚨 Known Issues & TODO

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

## 📞 Support

For issues and questions:
1. Check existing GitHub issues
2. Create new issue with detailed description
3. Contact development team

## 📄 License

This project is proprietary software developed for MIT Motorsports team.
