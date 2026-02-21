# 🚗 BlaBlaCar Clone

> A full-stack web application for finding and sharing rides, built with FastAPI (backend) and React + TypeScript (frontend).

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Features](#features)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Contributing](#contributing)
- [License](#license)

---

## 🌟 Overview

**BlaBlaCar Clone** is a ride-sharing platform that allows users to:

- 🔍 **Search for rides** between cities
- 🚙 **Create rides** as drivers
- 🤝 **Request to join** rides as passengers
- 👤 **Manage profiles** and view ride history
- 🔔 **Receive notifications** about trip updates

---

## 🛠 Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| [FastAPI](https://fastapi.tiangolo.com/) | Modern Python web framework |
| [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | ORM for database operations |
| [Pydantic v2](https://docs.pydantic.dev/) | Data validation |
| [Python-Jose](https://python-jose.readthedocs.io/) | JWT authentication |
| [Passlib](https://passlib.readthedocs.io/) | Password hashing |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server |

### Frontend

| Technology | Purpose |
|------------|---------|
| [React 18](https://react.dev/) | UI library |
| [TypeScript](https://www.typescriptlang.org/) | Type-safe JavaScript |
| [Vite](https://vitejs.dev/) | Build tool |
| [React Router](https://reactrouter.com/) | Client-side routing |
| [Axios](https://axios-http.com/) | HTTP client |
| [Zustand](https://zustand-demo.pmnd.rs/) | State management |

---

## 📁 Project Structure

```
bla-bla-car/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── trips.py
│   │   │   ├── requests.py
│   │   │   ├── users.py
│   │   │   └── notifications.py
│   │   ├── core/          # Configuration
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── main.py        # Application entry point
│   ├── tests/             # Test files
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
│
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   ├── stores/       # Zustand stores
│   │   ├── types/        # TypeScript types
│   │   ├── App.tsx       # Root component
│   │   └── main.tsx      # Entry point
│   ├── public/           # Static assets
│   ├── package.json      # Node dependencies
│   ├── tsconfig.json     # TypeScript config
│   └── vite.config.ts   # Vite config
│
├── docs/                   # Project documentation
│   ├── architecture.md
│   ├── API_CONTRACT.md
│   ├── AUTH_SPEC.md
│   └── ...
│
└── README.md              # This file
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **npm** or **pnpm** - Comes with Node.js

---

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the `backend/` directory:
   ```env
   DATABASE_URL=sqlite:///./app.db
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Run the backend server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   pnpm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   Open http://localhost:5173 in your browser

---

## ✨ Features

### Authentication
- ✅ User registration with email
- ✅ Secure login with JWT tokens
- ✅ Password hashing with bcrypt
- ✅ Protected routes

### Trips
- ✅ Create new trips (as driver)
- ✅ Search trips by origin, destination, and date
- ✅ View trip details
- ✅ Update and delete trips

### Ride Requests
- ✅ Send ride requests (as passenger)
- ✅ View pending requests (as driver)
- ✅ Approve or reject requests
- ✅ Track request status

### User Profile
- ✅ View user profiles
- ✅ Update profile information
- ✅ View ride history

### Notifications
- ✅ In-app notifications
- ✅ Read/unread status
- ✅ Real-time updates

---

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login and get JWT |
| `GET` | `/api/auth/me` | Get current user |

### Trip Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/trips` | Create a new trip |
| `GET` | `/api/trips` | Search trips |
| `GET` | `/api/trips/{id}` | Get trip details |
| `PUT` | `/api/trips/{id}` | Update trip |
| `DELETE` | `/api/trips/{id}` | Delete trip |

### Request Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/trips/{id}/request` | Send ride request |
| `GET` | `/api/requests` | Get my requests |
| `GET` | `/api/trips/{id}/requests` | Get trip requests |
| `PUT` | `/api/requests/{id}` | Handle request |

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/{id}` | Get user profile |
| `PUT` | `/api/users/{id}` | Update profile |
| `GET` | `/api/users/{id}/trips` | Get user trips |

---

## 🗄 Database Schema

### Users Table
```sql
users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  name VARCHAR NOT NULL,
  phone VARCHAR,
  avatar_url VARCHAR,
  rating DECIMAL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Trips Table
```sql
trips (
  id UUID PRIMARY KEY,
  driver_id UUID REFERENCES users(id),
  from_city VARCHAR NOT NULL,
  to_city VARCHAR NOT NULL,
  departure_date DATE NOT NULL,
  departure_time TIME NOT NULL,
  available_seats INTEGER NOT NULL,
  price_per_seat DECIMAL NOT NULL,
  description TEXT,
  status VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Trip Requests Table
```sql
trip_requests (
  id UUID PRIMARY KEY,
  trip_id UUID REFERENCES trips(id),
  passenger_id UUID REFERENCES users(id),
  seats_requested INTEGER,
  status VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Notifications Table
```sql
notifications (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  type VARCHAR,
  title VARCHAR,
  message TEXT,
  is_read BOOLEAN,
  related_trip_id UUID,
  related_request_id UUID,
  created_at TIMESTAMP
)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [BlaBlaCar](https://www.blablacar.com/) for inspiration

---

<div align="center">

Made with ❤️ by the Community

</div>
