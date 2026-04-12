# Library Management System — MVP (FastAPI backend + React frontend)

**Author:** Generated for you

**Purpose:** Step-by-step guide to build a minimum viable product (MVP) Library Management System (LMS) for a school using **FastAPI** (Python) for backend and **React** for frontend. This document includes setup, code structure, key endpoints, database schema, authentication, Docker, and testing instructions.

---

## Table of contents
1. Prerequisites
2. Project overview & features (MVP)
3. Tech stack
4. Project structure (recommended)
5. Backend (FastAPI) — step-by-step
   - Setup
   - Models & database
   - Schemas
   - CRUD & routers
   - Authentication (simple JWT)
   - Background tasks (overdue fines)
   - Testing
6. Frontend (React) — step-by-step
   - Setup
   - Pages & components
   - API integration
   - Authentication flow
7. Docker & docker-compose
8. Running the app locally
9. Sample requests (curl)
10. Tests & CI suggestions
11. Future enhancements / optional features
12. Appendix: Example snippets

---

## 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm or yarn
- Git
- Basic knowledge of Python, JavaScript, SQL
- (Optional) Docker & Docker Compose

---

## 2. Project overview & features (MVP)
MVP features to implement first:
- Add / update / delete books
- Register / view students (or library members)
- Issue book to a student
- Return book and calculate overdue fines
- Search books by title/author/ISBN
- Simple librarian authentication (email + password, JWT)
- Admin dashboard (basic) in React

---

## 3. Tech stack
- Backend: Python, FastAPI, SQLModel (or SQLAlchemy + Pydantic), Alembic (optional for migrations), SQLite for MVP
- Auth: PyJWT or `fastapi-jwt-auth` (or `fastapi-users` for more features)
- Frontend: React (Vite recommended), Axios / fetch
- Dev tooling: uvicorn, pytest
- Containerization: Docker, docker-compose

---

## 4. Project structure (recommended)
```
lms-mvp/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/            # config, settings
│   │   ├── db/              # db session, engine
│   │   ├── models/          # SQLModel / ORM models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # APIRouters: auth, books, members, issues
│   │   ├── services/        # business logic
│   │   └── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   ├── components/
│   │   └── services/api.js  # Axios wrapper
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 5. Backend (FastAPI) — step-by-step

### 5.1 Setup
1. Create a virtual environment and install packages:
```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlmodel[sqlite] alembic passlib[bcrypt] pyjwt python-dotenv
```
2. Create `backend/app/main.py` with FastAPI app instance and include routers.

### 5.2 Models & database (using SQLModel)
Create models in `app/models`:
```py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    isbn: Optional[str] = None
    total_copies: int = 1
    available_copies: int = 1
    added_at: datetime = Field(default_factory=datetime.utcnow)

class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    is_active: bool = True

class Issue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int
    member_id: int
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: date
    returned_at: Optional[datetime] = None
    fine: float = 0.0
```
Create engine and session helpers in `app/db`.

### 5.3 Schemas
Create Pydantic schemas (request/response) in `app/schemas` to separate model from API contract (create/update/read DTOs).

### 5.4 CRUD & routers
Implement CRUD operations for books, members and issue operations. Use APIRouter files under `app/routers/books.py`, `members.py`, `issues.py`.
- `POST /books` — add a book
- `GET /books` — list/search books (query params: q, author, isbn)
- `GET /books/{id}` — book detail
- `PUT /books/{id}` — update book
- `DELETE /books/{id}` — delete

Issuing logic (business rules):
- When issuing, check `available_copies` > 0 then decrement and create `Issue` record with `due_date` (e.g., +14 days).
- On return, set `returned_at`, compute fine = max(0, days_late * per_day_rate), increment `available_copies`.

### 5.5 Authentication (simple JWT)
- Keep `User` or `Librarian` table for credentials (hashed password using `passlib` bcrypt).
- Login endpoint returns JWT token. Protect routes with dependency that verifies JWT.

Example login flow:
- `POST /auth/login` — accept email & password -> return `{ access_token: "...", token_type: "bearer" }`
- Use `fastapi.security.OAuth2PasswordBearer` for dependency injection.

### 5.6 Background tasks (optional)
- Use a background job to compute overdue fines or send email reminders. For MVP, a scheduled cron job or an admin endpoint `/admin/check-overdues` is enough.

### 5.7 Testing
- Write pytest tests for endpoints, using `TestClient` from FastAPI and a temporary SQLite database.

---

## 6. Frontend (React) — step-by-step

### 6.1 Setup
Use Vite for a lightweight React app:
```bash
cd frontend
npm create vite@latest lms-frontend -- --template react
cd lms-frontend
npm install
npm install axios react-router-dom
```

### 6.2 Pages & components
- Pages: Login, Dashboard, BooksList, BookForm, MembersList, IssueBook, ReturnBook, Reports
- Components: Navbar, ProtectedRoute, BookCard, SearchBar

### 6.3 API integration
Create `src/services/api.js` with an Axios instance that attaches the JWT token from localStorage to `Authorization: Bearer <token>`.
Use fetch or axios for CRUD operations. Example endpoints:
- GET `/api/books` — display list
- POST `/api/books` — add book (admin)
- POST `/api/auth/login` — login

### 6.4 Authentication flow
- On login success, store token in `localStorage` and redirect to dashboard.
- Protect routes using a `ProtectedRoute` component; redirect to login if no token or token expired.

---

## 7. Docker & docker-compose
Create Dockerfile for backend and frontend. Example `docker-compose.yml` to run both services and a persistent SQLite (file mount) or Postgres if you prefer.

**docker-compose.yml (skeleton)**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=sqlite:///./data/lms.db
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

---

## 8. Running the app locally
1. Backend
```bash
cd backend
# start uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
2. Frontend
```bash
cd frontend
npm run dev
```

---

## 9. Sample requests (curl)
```bash
# Login
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"password"}'

# Add book
curl -X POST http://localhost:8000/books -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"title":"Maths","author":"A Author","total_copies":3}'
```

---

## 10. Tests & CI suggestions
- Use pytest for backend tests
- Use Github Actions to run tests on push and optionally build Docker images

---

## 11. Future enhancements / optional features
- Barcode/QR code generation and scanner support
- Role-based access (admin, assistant, student)
- Online catalog and public search
- Notifications (email/SMS) for overdue books
- Integrate an external identity provider (Google SSO)

---

## 12. Appendix: Example snippets
(Full code examples and templates for `main.py`, routers, and sample React components are available on request.)

---

*End of file.*

