# RoadMate

A full-stack web application for finding and sharing rides, built with FastAPI (backend) and React + TypeScript (frontend).

---

## Overview

BlaBlaCar Clone is a ride-sharing platform that allows users to:

- Search for rides between cities
- Create rides as drivers
- Request to join rides as passengers
- Manage profiles and view ride history
- Receive notifications about trip updates

---

## Prerequisites

Ensure you have the following installed on your system:

| Requirement | Version | Download Link |
|-------------|---------|----------------|
| Python | 3.10+ | [Python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [Nodejs.org](https://nodejs.org/) |
| npm | Comes with Node.js | - |

---

## Project Structure

```
BlaBlaCar/
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── trips.py       # Trip management endpoints
│   │   │   ├── requests.py    # Ride request endpoints
│   │   │   ├── users.py       # User management endpoints
│   │   │   └── notifications.py # Notification endpoints
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Application configuration
│   │   │   ├── security.py    # Security utilities
│   │   │   ├── database.py    # Database configuration
│   │   │   ├── logger.py      # Logging utilities
│   │   │   ├── middleware.py   # Custom middleware
│   │   │   └── exceptions.py  # Custom exceptions
│   │   ├── db/models/         # SQLAlchemy database models
│   │   ├── domain/            # Domain layer
│   │   │   └── enums.py       # Domain enums
│   │   ├── repositories/     # Repository pattern
│   │   │   ├── interfaces/   # Repository interfaces
│   │   │   └── inmemory/     # In-memory implementations
│   │   ├── services/         # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── trip_service.py
│   │   │   └── request_service.py
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── utils/            # Utilities
│   │   │   └── mappers.py    # Data mappers
│   │   ├── background/       # Background workers
│   │   │   ├── worker.py
│   │   │   └── adapters.py
│   │   └── main.py           # Application entry point
│   ├── tests/                # Test files
│   │   ├── unit/            # Unit tests
│   │   ├── integration/     # Integration tests
│   │   └── concurrency/     # Concurrency tests
│   ├── requirements.txt      # Python dependencies
│   └── .env                 # Environment variables
│
├── frontend/                  # React + TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── stores/           # Zustand state management
│   │   ├── types/            # TypeScript type definitions
│   │   ├── App.tsx          # Root component
│   │   └── main.tsx         # Entry point
│   ├── public/               # Static assets
│   ├── package.json         # Node dependencies
│   ├── tsconfig.json        # TypeScript configuration
│   └── vite.config.ts       # Vite configuration
│
└── README.md                 # This file
```

---

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (optional but recommended):

   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **Linux/MacOS:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:

   Create a `.env` file in the `backend/` directory with the following content:
   ```env
   # Application Settings
   APP_NAME=Ride Sharing API
   DEBUG=True

   # JWT Settings
   JWT_SECRET_KEY=your-secret-key-change-in-production
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

   # CORS
   ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]

   # Database
   USE_POSTGRESQL=False
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

---

## Running the Application

### Starting the Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

The backend server will start on http://localhost:8000

### Starting the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

The frontend application will start on http://localhost:5173

### Accessing the Application

Open your web browser and navigate to:
```
http://localhost:5174
```

---

## Features

### Authentication
- User registration with email
- Secure login with JWT tokens
- Refresh token support
- Password hashing with bcrypt
- Protected routes

### Trips
- Create new trips (as driver)
- Search trips by origin, destination, and date
- View trip details
- Update and delete trips
- Trip status management (active, completed, cancelled)

### Ride Requests
- Send ride requests (as passenger)
- View pending requests (as driver)
- Approve or reject requests
- Track request status
- Concurrent request handling

### User Profile
- View user profiles
- Update profile information
- View ride history

### Notifications
- In-app notifications
- Read/unread status
- Real-time notification updates

---

## API Documentation

Once the backend is running, you can access the API documentation at:

| Documentation | URL |
|---------------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login and get JWT |
| GET | /api/auth/me | Get current user |

### Trip Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/trips | Create a new trip |
| GET | /api/trips | Search trips |
| GET | /api/trips/{id} | Get trip details |
| PUT | /api/trips/{id} | Update trip |
| DELETE | /api/trips/{id} | Delete trip |

### Request Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/trips/{id}/request | Send ride request |
| GET | /api/requests | Get my requests |
| GET | /api/trips/{id}/requests | Get trip requests |
| PUT | /api/requests/{id} | Handle request |

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/users/{id} | Get user profile |
| PUT | /api/users/{id} | Update profile |
| GET | /api/users/{id}/trips | Get user trips |

---

## Troubleshooting

### Port Already in Use

If port 8000 or 5173 is already in use, you can specify a different port:

**Backend:**
```bash
uvicorn app.main:app --reload --port 8001
```

**Frontend:**
```bash
npm run dev -- --port 5174
```

### Dependency Installation Errors

If you encounter errors during dependency installation:

```bash
# Update pip
python -m pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt
```

### Backend Not Responding

Ensure the backend is running and check the terminal for error messages. The backend should display:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Technology Stack

### Backend
- FastAPI - Modern Python web framework
- SQLAlchemy 2.0 - ORM for database operations
- Pydantic v2 - Data validation
- Python-Jose - JWT authentication
- Passlib - Password hashing
- Uvicorn - ASGI server
- Repository Pattern - Data access abstraction
- Background Workers - Async task processing

### Frontend
- React 18 - UI library
- TypeScript - Type-safe JavaScript
- Vite - Build tool
- React Router - Client-side routing
- Axios - HTTP client
- Zustand - State management

---

## Architecture

This project follows a layered architecture pattern:

### Backend Layers
1. **API Layer** (`app/api/`) - FastAPI route handlers
2. **Service Layer** (`app/services/`) - Business logic
3. **Repository Layer** (`app/repositories/`) - Data access abstraction
4. **Domain Layer** (`app/domain/`) - Domain models and enums
5. **Database Models** (`app/db/models/`) - SQLAlchemy models

### Testing
The project includes comprehensive tests:
- **Unit Tests** - Testing individual components in isolation
- **Integration Tests** - Testing component interactions
- **Concurrency Tests** - Testing thread-safe operations

Run tests with:
```bash
pytest
```

---

## License

This project is licensed under the MIT License.
