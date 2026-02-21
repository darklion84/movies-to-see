# External Integrations

**Analysis Date:** 2026-02-18

## APIs & External Services

**The Movie Database (TMDB):**
- Service: TMDB API v3 - Movie and TV show metadata, search, and credits
  - What it's used for: Search movies/TV shows, retrieve full details (poster, rating, cast, release date)
  - SDK/Client: `httpx` (async HTTP client)
  - Auth: Environment variable `TMDB_API_KEY` (passed as `api_key` query param)
  - Base URL: `https://api.themoviedb.org/3`
  - Image URL: `https://image.tmdb.org/t/p/w500` (for poster paths)

**Implementation files:**
- `backend/tmdb.py` - TMDB client with two async functions:
  - `search_movies(query)` - Searches multi-type endpoint, filters to movie/tv only, returns top 10
  - `get_movie_details(tmdb_id, media_type)` - Fetches single movie/tv with credits, extracts top 5 cast
- `backend/main.py` - Routes that call TMDB:
  - `GET /api/search?q=...` - Calls `search_movies()`
  - `POST /api/movies` - Calls `get_movie_details()` to fetch metadata before storing

## Data Storage

**Databases:**
- SQLite 3 (local file-based database)
  - Connection: `sqlite:///./movies.db` (in `backend/database.py`)
  - ORM: SQLAlchemy 2.0+
  - Model: `Movie` class in `backend/database.py` with columns:
    - `id` (primary key)
    - `tmdb_id` (unique, indexed)
    - `title`, `description`, `poster_url`, `rating`
    - `release_year`, `actors`, `media_type` (movie/tv)
    - `watched` (boolean), `impression` (liked/ok/disliked)
    - `added_at`, `watched_at` (timestamps)

**File Storage:**
- None - No external file storage service used
- Static assets: Built frontend served from `frontend/dist/` directory by FastAPI

**Caching:**
- None - No caching layer (Redis, Memcached, etc.)

## Authentication & Identity

**Auth Provider:**
- Custom implementation using JWT
  - Implementation: `backend/auth.py`
  - Scheme: HTTP Bearer token in `Authorization` header
  - Algorithm: HS256 (symmetric key)
  - Duration: 30 days (from `ACCESS_TOKEN_EXPIRE_DAYS`)
  - Secret key: Environment variable `SECRET_KEY`

**Login Flow:**
1. Client sends password to `POST /api/login`
2. Password verified against `APP_PASSWORD` environment variable (simple string comparison in `verify_password()`)
3. JWT token created with 30-day expiration
4. Token stored in browser localStorage (frontend)
5. Token included in `Authorization: Bearer <token>` header for all subsequent requests
6. Token validated on each protected endpoint via `get_current_user()` dependency

**Protected Endpoints:**
- `GET /api/movies`
- `POST /api/movies`
- `DELETE /api/movies/{id}`
- `GET /api/search`
- `PATCH /api/movies/{id}/watched`
- `PATCH /api/movies/{id}/unwatched`

## Monitoring & Observability

**Error Tracking:**
- None - No dedicated error tracking service (Sentry, Datadog, etc.)

**Logs:**
- stdout/stderr only - No structured logging service
- Development: Uvicorn logs to console
- No log aggregation or persistence

## CI/CD & Deployment

**Hosting:**
- Self-hosted (local or standalone server)
- `run.sh` script handles local development and production startup
- Builds and serves single unified binary/process

**CI Pipeline:**
- None - No automated CI/CD detected

## Environment Configuration

**Required env vars:**
- `TMDB_API_KEY` - The Movie Database API key (from https://www.themoviedb.org/settings/api)
- `APP_PASSWORD` - Simple password for login (single-user auth)
- `SECRET_KEY` - Random secret for JWT signing (must be kept private)

**Secrets location:**
- `backend/.env` - Local file (git-ignored, not committed)
- Template: `backend/.env.example` shows required format

**Loading:**
- `python-dotenv` loads `.env` on backend startup in `main.py` via `load_dotenv()`

## Webhooks & Callbacks

**Incoming:**
- None - No external webhooks received

**Outgoing:**
- None - No outbound webhooks sent

## CORS & API Access

**CORS Configuration:**
- Enabled with permissive settings in `backend/main.py`:
  - `allow_origins=["*"]` - Accept requests from any origin
  - `allow_methods=["*"]` - Accept all HTTP methods
  - `allow_headers=["*"]` - Accept all headers
- Suitable for localhost development; should be restricted in production

## Frontend-Backend Communication

**Proxy:**
- Development: Vite dev server proxies `/api/*` to `http://localhost:8000` (from `frontend/vite.config.js`)
- HTTP Client: Fetch API (no external HTTP library in frontend)
- Token Management: Token stored in `localStorage`, injected as `Authorization: Bearer <token>` header
- Error Handling: 401/403 responses clear token and throw error

**API Base:**
- Frontend: `/api` (relative path, proxied in dev)
- Actual endpoint: `http://localhost:8000/api` in production

---

*Integration audit: 2026-02-18*
