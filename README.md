# Task Management API 🚀
> A robust, production-ready RESTful API built with **Django 5.x**, **Django REST Framework (DRF)**, and **SimpleJWT**. Designed with multi-tenant data isolation, role-based resource ownership, high-performance query optimization, full-text search, dynamic filtering, and production deployment configuration for Render & PostgreSQL.

---

## 🛠️ Tech Stack & Architecture

- **Backend Framework**: Python 3.11+ / Django 5.x
- **API Engine**: Django REST Framework (DRF)
- **Authentication**: JSON Web Tokens (`djangorestframework-simplejwt`)
- **Query Filtering**: `django-filter` (Exact & Choice filter sets)
- **Environment Management**: `python-decouple`
- **Database Engine**: `dj-database-url` (SQLite for local dev, PostgreSQL for production)
- **WSGI Production Server**: Gunicorn
- **Static Assets Serving**: WhiteNoise

---

## 📁 Project Structure

```text
task-management-api/
├── config/                  # Django project root configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # Dynamic decouple & DB URL configuration
│   ├── urls.py             # Global routing & root health checks
│   └── wsgi.py
├── users/                   # Authentication & user profile app
│   ├── apps.py
│   ├── serializers.py      # Registration with password confirmation & hashing
│   ├── tests.py            # APITestCase for Auth & JWT flow
│   ├── urls.py             # Auth endpoints (/register/, /login/, /refresh/)
│   └── views.py            # Public registration view
├── tasks/                   # Core business logic app
│   ├── admin.py            # Django Admin registrations
│   ├── apps.py
│   ├── filters.py          # Custom django-filter FilterSet class
│   ├── models.py           # Project & Task models with DB indexes
│   ├── pagination.py       # Standard PageNumberPagination (10/page)
│   ├── permissions.py      # IsOwner object-level permission class
│   ├── serializers.py      # Project & Task serializers with tenant validation
│   ├── tests.py            # APITestCase for CRUD, filtering, & tenant isolation
│   ├── urls.py             # DefaultRouter endpoints for projects & tasks
│   └── views.py            # ModelViewSets with N+1 query prevention
├── staticfiles/             # Collected static files for WhiteNoise
├── .env.example             # Example environment variables template
├── .gitignore               # Git ignore rules
├── manage.py
└── requirements.txt         # Pinned production dependencies
```

---

## ⚙️ Local Development Setup

### 1. Clone repository & create virtual environment
```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup environment variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-local-secret-key-12345
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
# Leave DATABASE_URL commented to use SQLite locally
# DATABASE_URL=postgres://user:password@localhost:5432/taskdb
```

### 4. Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser (Optional for Django admin)
```bash
python manage.py createsuperuser
```

### 6. Run unit tests
```bash
python manage.py test
```

### 7. Start local server
```bash
python manage.py runserver
```
API root is accessible at: `http://127.0.0.1:8000/`

---

## 🔐 Environment Variables

| Variable | Local Default | Production (Render) | Purpose |
| :--- | :--- | :--- | :--- |
| `SECRET_KEY` | local insecure key | High-entropy random string | Cryptographic signing key |
| `DEBUG` | `True` | `False` | Enables/Disables debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | `.onrender.com,your-domain.com` | Allowed host headers |
| `DATABASE_URL` | *None (defaults to SQLite)* | `postgres://user:pass@host:5432/db` | Connection string for PostgreSQL |

---

## 📡 API Endpoints Reference

| Method | URL | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| **GET** | `/` | ❌ No | Health check and API root index |
| **POST** | `/api/register/` | ❌ No | Register new user account (hashes password) |
| **POST** | `/api/login/` | ❌ No | Obtain JWT Access and Refresh tokens |
| **POST** | `/api/token/refresh/` | ❌ No | Obtain new Access token using Refresh token |
| **GET** | `/api/projects/` | ✅ Bearer | List projects owned by the user (with `task_count`) |
| **POST** | `/api/projects/` | ✅ Bearer | Create a new project (auto-assigned to user) |
| **GET** | `/api/projects/{id}/` | ✅ Bearer | Retrieve specific project details and task count |
| **PUT/PATCH** | `/api/projects/{id}/` | ✅ Bearer | Update project details (owner only) |
| **DELETE** | `/api/projects/{id}/` | ✅ Bearer | Delete project and cascade tasks (owner only) |
| **GET** | `/api/tasks/` | ✅ Bearer | List user tasks (supports filter, search, sort, pagination) |
| **POST** | `/api/tasks/` | ✅ Bearer | Create task (validates project belongs to user) |
| **GET** | `/api/tasks/{id}/` | ✅ Bearer | Retrieve specific task details |
| **PUT/PATCH** | `/api/tasks/{id}/` | ✅ Bearer | Update task status, priority, or details |
| **DELETE** | `/api/tasks/{id}/` | ✅ Bearer | Delete specific task |

---

## 💡 Query Parameters for `/api/tasks/`

1. **Filtering**:
   - Status: `/api/tasks/?status=done` (`todo`, `in_progress`, `done`)
   - Priority: `/api/tasks/?priority=high` (`low`, `medium`, `high`)
   - Project: `/api/tasks/?project=1`
   - Combined: `/api/tasks/?status=done&priority=high&project=1`
2. **Search**:
   - `/api/tasks/?search=database` (searches `title` and `description`)
3. **Ordering**:
   - `/api/tasks/?ordering=due_date` (Ascending)
   - `/api/tasks/?ordering=-due_date` (Descending)
4. **Pagination**:
   - `/api/tasks/?page=2` (10 items per page)
   - `/api/tasks/?page=1&page_size=20`

---

## 📦 Sample Request & Response Payloads

### 1. Register User
`POST /api/register/`
```json
// Request Body
{
  "username": "junior_dev",
  "email": "dev@example.com",
  "password": "SuperSecretPassword123!",
  "password2": "SuperSecretPassword123!"
}

// Response (201 Created)
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "username": "junior_dev",
    "email": "dev@example.com"
  }
}
```

### 2. Login (Obtain JWT)
`POST /api/login/`
```json
// Request Body
{
  "username": "junior_dev",
  "password": "SuperSecretPassword123!"
}

// Response (200 OK)
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3. Create Project
`POST /api/projects/`
*Header: `Authorization: Bearer <access_token>`*
```json
// Request Body
{
  "name": "Backend Portfolio",
  "description": "Production-ready Django REST Framework APIs"
}

// Response (201 Created)
{
  "id": 1,
  "name": "Backend Portfolio",
  "description": "Production-ready Django REST Framework APIs",
  "owner": "junior_dev",
  "task_count": 0,
  "created_at": "2026-10-29T04:45:00.000000Z",
  "updated_at": "2026-10-29T04:45:00.000000Z"
}
```

### 4. Create Task
`POST /api/tasks/`
*Header: `Authorization: Bearer <access_token>`*
```json
// Request Body
{
  "title": "Implement JWT Auth & Refresh",
  "description": "Integrate SimpleJWT with 60 min token rotation",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2026-11-05T18:00:00Z",
  "project": 1
}

// Response (201 Created)
{
  "id": 1,
  "title": "Implement JWT Auth & Refresh",
  "description": "Integrate SimpleJWT with 60 min token rotation",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2026-11-05T18:00:00Z",
  "project": 1,
  "project_name": "Backend Portfolio",
  "assigned_to": null,
  "assigned_to_username": null,
  "created_at": "2026-10-29T04:50:00.000000Z",
  "updated_at": "2026-10-29T04:50:00.000000Z"
}
```

### 5. List Projects (Nested task_count)
`GET /api/projects/`
*Header: `Authorization: Bearer <access_token>`*
```json
// Response (200 OK)
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Backend Portfolio",
      "description": "Production-ready Django REST Framework APIs",
      "owner": "junior_dev",
      "task_count": 1,
      "created_at": "2026-10-29T04:45:00.000000Z",
      "updated_at": "2026-10-29T04:45:00.000000Z"
    }
  ]
}
```

---

## 🧪 Postman Step-by-Step Test Order

To test the entire workflow end-to-end in Postman:

1. **Register User A**:
   - `POST http://127.0.0.1:8000/api/register/`
   - Store credentials for User A.
2. **Login User A**:
   - `POST http://127.0.0.1:8000/api/login/`
   - Save returned `access` token as an environment variable `{{token_a}}`.
3. **Create Project as User A**:
   - `POST http://127.0.0.1:8000/api/projects/`
   - Auth: `Bearer {{token_a}}`
   - Body: `{"name": "Alice Project", "description": "Alice's scope"}`
   - Save created project ID (e.g. `1`).
4. **Create Tasks as User A**:
   - `POST http://127.0.0.1:8000/api/tasks/`
   - Auth: `Bearer {{token_a}}`
   - Body: `{"title": "Task 1", "status": "todo", "priority": "high", "project": 1}`
5. **Register & Login User B**:
   - Register `user_b` and obtain `{{token_b}}`.
6. **Verify Data Isolation (Security)**:
   - `GET /api/projects/` using `Bearer {{token_b}}` -> Returns 0 projects!
   - `GET /api/tasks/` using `Bearer {{token_b}}` -> Returns 0 tasks!
   - `GET /api/projects/1/` using `Bearer {{token_b}}` -> Returns **404 Not Found**.
   - `POST /api/tasks/` using `Bearer {{token_b}}` with `"project": 1` -> Returns **400 Bad Request** with message: *"You cannot associate a task with a project you do not own."*
7. **Test Filter, Search & Ordering as User A**:
   - `/api/tasks/?status=todo`
   - `/api/tasks/?priority=high`
   - `/api/tasks/?search=Task`
   - `/api/tasks/?ordering=due_date`
8. **Test Refresh Token**:
   - `POST /api/token/refresh/` with `{"refresh": "<refresh_token>"}` -> Returns a fresh `access` token.

---

## 🚀 Render Deployment Guide

Follow these steps to deploy this project to **Render** with a Managed PostgreSQL database:

### 1. Create a PostgreSQL Database on Render
1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **PostgreSQL**.
3. Set Name to `task-manager-db`.
4. Click **Create Database**.
5. Once created, copy the **Internal Database URL** (e.g., `postgres://user:password@hostname:5432/dbname`).

### 2. Deploy Web Service on Render
1. Click **New +** -> **Web Service**.
2. Connect your GitHub repository containing this project.
3. Configure settings:
   - **Name**: `task-management-api`
   - **Environment**: `Python 3`
   - **Region**: Choose the same region as your database.
   - **Branch**: `main`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**:
     ```bash
     gunicorn config.wsgi:application
     ```

### 3. Add Environment Variables in Render Dashboard
Go to **Environment** tab in your Web Service and add:

| Key | Value |
| :--- | :--- |
| `PYTHON_VERSION` | `3.11.9` (or `3.12.x` / `3.13.x`) |
| `SECRET_KEY` | Generate a long random secret string |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `DATABASE_URL` | *Paste the Internal Database URL from Step 1* |

### 4. Verify Production Deployment
- Once the build finishes, open `https://your-service-name.onrender.com/`.
- You will see the root health check JSON confirming the system is running live on PostgreSQL and WhiteNoise is serving static assets!

