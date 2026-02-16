# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
```bash
# Backend (from backend/)
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Frontend (from frontend/)
npm run dev          # Dev server on port 5173
npm run build        # Build to dist/
```

### Testing
```bash
# Backend tests
cd backend && pytest -v

# Single test
pytest tests/test_api.py::test_login -v

# Frontend tests
cd frontend && npm test
```

### Production
```bash
./run.sh  # Builds frontend and starts backend on port 8000
```

## Architecture

**Backend (FastAPI + SQLAlchemy + SQLite)**
- `main.py` - API routes and Pydantic models, serves built frontend from `frontend/dist/`
- `database.py` - SQLAlchemy Movie model and CRUD operations
- `tmdb.py` - TMDB API client for movie search and details
- `auth.py` - JWT authentication with single password (from `APP_PASSWORD` env var)

**Frontend (Vue 3 + Vite)**
- `App.vue` - Main component with tabs (to watch / watched), modals, and movie list
- `api.js` - HTTP client for backend API with JWT token handling
- Components: `AddMovie`, `MovieCard`, `MovieList`, `MovieModal`, `RatingModal`, `LoginForm`

**Data Flow**
1. User searches movies → `AddMovie` calls `/api/search` → TMDB API
2. User selects movie → `/api/movies` POST → stored in SQLite with TMDB data
3. User marks watched → `/api/movies/{id}/watched` PATCH with impression (liked/ok/disliked)
4. Movie cards show watch date and impression icon for watched movies

## Migrations

After pulling updates, run any new migrations:
```bash
cd backend
sqlite3 movies.db < migrations/001_add_media_type.sql
```

## Configuration

Backend requires `backend/.env`:
```
TMDB_API_KEY=...
APP_PASSWORD=...
SECRET_KEY=...
```
