# IS601 Final Project

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/rafaelwastaken/is601-fiinal-project/ci-cd.yml?branch=master)](https://github.com/rafaelwastaken/is601-fiinal-project/actions/workflows/ci-cd.yml)
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/rafaelwastaken/is601-final-project)](https://hub.docker.com/r/rafaelwastaken/is601-final-project)

FastAPI calculator app with JWT authentication, protected calculation BREAD routes, and an account password-change flow

## Project Structure

```text
app/
  crud/         # database operations
  db/           # SQLAlchemy engine/session
  factories/    # calculation factory logic
  models/       # SQLAlchemy models (user, calculation)
  schemas/      # Pydantic schemas
  static/       # login/register/account/calculations frontend pages and assets
  main.py       # FastAPI routes (health, auth, users, password change, calculations)
tests/
  unit/         # unit tests
  integration/  # API integration tests
  e2e/          # Playwright browser tests
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (CLI or Desktop) for running the containers locally

## Local Setup

### Python dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Node dependencies (Playwright)

```powershell
npm ci
npx playwright install chromium
```

## Run the API Locally

Default database is SQLite (`app.db`) when `DATABASE_URL` is not set.

```powershell
uvicorn app.main:app --reload
```

Health check: http://127.0.0.1:8000/health

OpenAPI docs:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Local test database

Integration tests use PostgreSQL. Set `TEST_DATABASE_URL` to a local Postgres instance before running them.

Example:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/module12_test"
```

## Front-End Pages

- Registration page: http://127.0.0.1:8000/register.html
- Login page: http://127.0.0.1:8000/login.html
- Account page: http://127.0.0.1:8000/account.html
- Calculations dashboard: http://127.0.0.1:8000/calculations.html

Client-side behavior:

- Email format validation
- Minimum password length validation (8)
- Confirm password validation on register page
- JWT token stored in `localStorage` key `jwt_token` on success
- Login button only appears for logged-out users
- Logout button only appears for logged-in users
- Protected pages redirect to login when the session is missing or invalid
- Calculation input validation (number checks, allowed operation types, divide-by-zero guard)
- Password change validation on the account page

## API Endpoints

### JWT Auth

- `POST /register` with `email` and `password`
- `POST /login` with `email` and `password`
- `GET /users/me` returns the current user profile
- `POST /users/me/password` changes the current user password

Successful responses return:

- `access_token`
- `token_type` (`bearer`)

### Existing User Routes

- `POST /users/register`
- `POST /users/login`

### Calculations

- `GET /calculations` browse current user's calculations
- `GET /calculations/{id}` read one calculation by ID (current user only)
- `POST /calculations` add a new calculation
- `PUT /calculations/{id}` edit an existing calculation
- `DELETE /calculations/{id}` delete a calculation

Notes:

- These routes require `Authorization: Bearer <jwt>`
- Access to another user's calculations returns not found
- Password changes require the current password and update the stored hash

## Running Tests Locally

### Run all Python tests

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/module12_test"
pytest tests/unit tests/integration
```

### Run Playwright E2E tests

Start the API first (local or Docker), then run:

```powershell
npm.cmd run test:e2e
```

Covered E2E scenarios include:

- Positive: register/login, create/read/update/delete calculations, password change and re-login
- Negative: invalid credentials, invalid inputs, unauthorized/missing token, invalid token, wrong current password

## Docker

### Build and run services

```powershell
docker compose up --build
```

### Build and run the API locally against Postgres

```powershell
docker compose up -d --build api
```

### Run detached

```powershell
docker compose up -d
```

### Stop services

```powershell
docker compose down
```

Services:

- `db`: PostgreSQL 16
- `api`: FastAPI app on port `8000`
