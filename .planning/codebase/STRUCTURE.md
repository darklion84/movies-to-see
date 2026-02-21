# Codebase Structure

**Analysis Date:** 2026-02-18

## Directory Layout

```
movies_to_see/
├── backend/                  # FastAPI backend application
│   ├── auth.py              # JWT authentication and token management
│   ├── database.py          # SQLAlchemy ORM and CRUD operations
│   ├── main.py              # FastAPI app, routes, Pydantic models
│   ├── tmdb.py              # TMDB API client for search and details
│   ├── migrations/          # SQL migration scripts
│   │   └── 001_add_media_type.sql
│   ├── tests/               # Backend test suite
│   │   ├── __init__.py
│   │   ├── conftest.py      # Pytest fixtures and config
│   │   ├── test_api.py      # API endpoint tests
│   │   ├── test_database.py # Database function tests
│   │   └── test_tmdb.py     # TMDB client tests
│   ├── .env                 # Environment variables (not committed)
│   ├── .env.example         # Example environment template
│   ├── movies.db            # SQLite database file
│   └── requirements.txt     # Python dependencies
├── frontend/                # Vue 3 + Vite frontend application
│   ├── src/                 # Source code
│   │   ├── main.js          # Vue app initialization
│   │   ├── api.js           # HTTP client and API functions
│   │   ├── App.vue          # Main app component (container)
│   │   └── components/      # Reusable Vue components
│   │       ├── AddMovie.vue       # Search and add movie form
│   │       ├── LoginForm.vue      # Password authentication
│   │       ├── MovieCard.vue      # Individual movie display
│   │       ├── MovieList.vue      # Grid layout of cards
│   │       ├── MovieModal.vue     # Movie detail modal
│   │       ├── RatingModal.vue    # Impression (watched) selector
│   │       └── __tests__/
│   │           └── MovieList.spec.js  # Component tests
│   ├── dist/                # Built production files (generated)
│   ├── package.json         # npm dependencies and scripts
│   ├── package-lock.json    # Locked dependency versions
│   ├── vite.config.js       # Vite bundler configuration
│   └── index.html           # HTML entry point
├── .planning/
│   └── codebase/            # Analysis documents
├── venv/                    # Python virtual environment
├── CLAUDE.md                # Project guidance for Claude
├── README.md                # Project documentation
├── run.sh                   # Production startup script
└── .gitignore               # Git ignore rules
```

## Directory Purposes

**backend/**
- Purpose: Python FastAPI REST API server
- Contains: Route handlers, business logic, database models, external API clients
- Key files: `main.py` (routes), `database.py` (models/CRUD), `auth.py` (JWT), `tmdb.py` (search)

**frontend/**
- Purpose: Vue 3 single-page application
- Contains: Vue components, HTTP client, styling
- Key files: `App.vue` (main container), `components/` (reusable widgets)

**backend/migrations/**
- Purpose: Database schema change scripts
- Contains: SQL files executed after pulling updates
- Key files: `001_add_media_type.sql` (adds media_type column for TV support)

**backend/tests/**
- Purpose: Automated test suite for backend
- Contains: Pytest test files with fixtures
- Key files: `conftest.py` (shared fixtures), `test_api.py` (endpoint tests)

**frontend/src/components/__tests__/**
- Purpose: Frontend component tests
- Contains: Jest/Vitest test files
- Key files: `MovieList.spec.js`

## Key File Locations

**Entry Points:**
- `backend/main.py`: FastAPI application definition, route handlers, app startup
- `frontend/src/main.js`: Vue app initialization and DOM mounting
- `frontend/index.html`: HTML shell that loads Vue app

**Configuration:**
- `backend/.env`: Environment variables (TMDB_API_KEY, APP_PASSWORD, SECRET_KEY)
- `frontend/vite.config.js`: Build and dev server config, API proxy setup
- `backend/requirements.txt`: Python package dependencies

**Core Logic:**
- `backend/database.py`: Movie model, CRUD operations, database session
- `backend/auth.py`: JWT token generation and validation
- `backend/tmdb.py`: TMDB API integration for search and details
- `frontend/src/api.js`: HTTP client, token management, API function wrappers

**Data:**
- `backend/movies.db`: SQLite database with movies table

**Migrations:**
- `backend/migrations/001_add_media_type.sql`: Schema migration to support TV shows

## Naming Conventions

**Files:**
- Backend Python: `snake_case.py` (e.g., `tmdb.py`, `auth.py`, `database.py`)
- Frontend Vue components: `PascalCase.vue` (e.g., `AddMovie.vue`, `MovieCard.vue`)
- Frontend JavaScript: `camelCase.js` (e.g., `api.js`, `main.js`)
- Tests: `test_<module>.py` (backend) or `<component>.spec.js` (frontend)
- Migrations: `<sequence>_<description>.sql` (e.g., `001_add_media_type.sql`)

**Directories:**
- Backend feature areas: `snake_case` (migrations, tests)
- Frontend feature areas: `components` (reusable widgets)
- Generated directories: `dist` (built frontend), `__pycache__`, `node_modules`

**Variables/Functions:**
- Backend functions: `snake_case` (create_movie, get_all_movies, mark_as_watched)
- Frontend methods: `camelCase` (onLoginSuccess, loadMovies, handleDelete)
- Vue component names: `PascalCase` (LoginForm, MovieCard)
- Computed properties: `camelCase` (toWatchMovies, displayedMovies)

**Database/API:**
- Table names: lowercase (movies)
- Column names: snake_case (tmdb_id, poster_url, watched_at, release_year)
- API endpoints: `/api/<resource>` or `/api/<resource>/<id>/<action>` (e.g., `/api/movies`, `/api/movies/1/watched`)
- JSON keys in requests/responses: snake_case (tmdb_id, media_type)

## Where to Add New Code

**New Feature:**
- Primary code: Add route to `backend/main.py`, add/update CRUD function in `backend/database.py`, add API function to `frontend/src/api.js`, add component/logic to `frontend/src/App.vue` or new component in `frontend/src/components/`
- Tests: Add `backend/tests/test_<module>.py` for backend, add `frontend/src/components/__tests__/<Component>.spec.js` for frontend

**New Component/Module:**
- Implementation: `backend/<module>.py` for backend modules, `frontend/src/components/<ComponentName>.vue` for reusable components
- Include: Pydantic models in `main.py` for API data contracts

**Utilities/Helpers:**
- Shared helpers: Create in logical location (e.g., `backend/utils.py`, `frontend/src/utils.js`)
- Backend utilities: Import in `main.py` or feature modules
- Frontend utilities: Import in `api.js` or components as needed

**Database Changes:**
- Schema changes: Always create new migration file `backend/migrations/<sequence>_<description>.sql`
- Model updates: Modify `Movie` class in `backend/database.py`
- CRUD functions: Add to `backend/database.py`
- Pydantic models: Add/update in `backend/main.py` or import from database

## Special Directories

**frontend/dist/:**
- Purpose: Built production frontend files
- Generated: Yes (via `npm run build`)
- Committed: No (in .gitignore)
- Served by: Backend via `/assets` mount and catchall SPA route

**backend/venv/:**
- Purpose: Python virtual environment with installed packages
- Generated: Yes (via `python -m venv venv`)
- Committed: No (in .gitignore)
- Activation: `source backend/venv/bin/activate` (macOS/Linux)

**frontend/node_modules/:**
- Purpose: npm package dependencies
- Generated: Yes (via `npm install`)
- Committed: No (in .gitignore)
- Managed by: `package-lock.json` ensures reproducible installs

**backend/.pytest_cache/:**
- Purpose: Pytest cache for faster test discovery
- Generated: Yes (automatic on `pytest` run)
- Committed: No (in .gitignore)
- Safe to delete: Yes, regenerated on next test run

---

*Structure analysis: 2026-02-18*
