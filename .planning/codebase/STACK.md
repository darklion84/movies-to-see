# Technology Stack

**Analysis Date:** 2026-02-18

## Languages

**Primary:**
- Python 3 - Backend API with FastAPI
- JavaScript (ES6 modules) - Frontend with Vue 3

**Secondary:**
- SQL (SQLite) - Database queries and migrations

## Runtime

**Environment:**
- Python 3.x (with venv virtual environment)
- Node.js (for npm package management)

**Package Manager:**
- `pip` - Python package management
  - Lockfile: Not used; uses `requirements.txt` with pinned versions
- `npm` - JavaScript package management
  - Lockfile: `frontend/package-lock.json` present

## Frameworks

**Core:**
- FastAPI 0.109.0+ - REST API framework for backend
- Vue 3 (^3.4.15) - Frontend framework
- Vite (^5.0.11) - Frontend build tool and dev server

**Testing:**
- pytest 8.0.0+ - Python unit and integration tests
- pytest-asyncio 0.23.3+ - Async test support for FastAPI
- vitest (^1.2.1) - JavaScript test runner
- @vue/test-utils (^2.4.4) - Vue component testing utilities
- jsdom (^24.0.0) - DOM environment for JavaScript tests

**Build/Dev:**
- @vitejs/plugin-vue (^5.0.3) - Vue support in Vite
- Uvicorn 0.27.0+ - ASGI server for FastAPI

## Key Dependencies

**Critical:**
- SQLAlchemy (>=2.0.36) - ORM for database operations; used in `backend/database.py`
- httpx (>=0.26.0) - Async HTTP client; used in `backend/tmdb.py` for TMDB API calls
- python-jose[cryptography] (>=3.3.0) - JWT token creation and verification; used in `backend/auth.py`
- python-dotenv (>=1.0.0) - Environment variable loading from `.env`

**Infrastructure:**
- passlib (>=1.7.4) - Password handling utilities (available but minimal usage in current codebase)

## Configuration

**Environment:**
- Environment variables configured via `.env` file in backend directory
- Required vars: `TMDB_API_KEY`, `APP_PASSWORD`, `SECRET_KEY`
- Example template: `backend/.env.example`

**Build:**
- `frontend/vite.config.js` - Vite configuration with Vue plugin and dev proxy to backend
  - Dev proxy: `/api` requests routed to `http://localhost:8000`
  - Test environment: jsdom

**Backend:**
- `backend/main.py` - FastAPI app initialization and route definitions
- Database: SQLite (`movies.db`) created automatically with SQLAlchemy on startup

## Platform Requirements

**Development:**
- Python 3.x with pip
- Node.js with npm
- SQLite 3 (usually included with Python)
- Bash shell (for `run.sh` script)

**Production:**
- Python 3.x runtime
- Node.js (if building frontend; optional if pre-built)
- SQLite database file (`movies.db`)
- Environment variables: `TMDB_API_KEY`, `APP_PASSWORD`, `SECRET_KEY`

## Database

**Type:** SQLite 3
**Location:** `backend/movies.db` (created on first startup)
**ORM:** SQLAlchemy 2.0+
**Schema Management:** Manual migrations in `backend/migrations/` (e.g., `001_add_media_type.sql`)

## Server

**Backend Server:**
- Framework: FastAPI
- Server: Uvicorn (ASGI)
- Port: 8000
- Host: 0.0.0.0 (configurable)
- Static files: Serves built frontend from `frontend/dist/`

**Frontend Dev Server:**
- Framework: Vite
- Port: 5173 (default)
- Proxy: `/api` requests forwarded to backend at port 8000

---

*Stack analysis: 2026-02-18*
