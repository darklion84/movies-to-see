# Architecture

**Analysis Date:** 2026-02-18

## Pattern Overview

**Overall:** Full-stack Single-Page Application with REST API backend and frontend

**Key Characteristics:**
- Separation between FastAPI backend (Python) and Vue 3 frontend (JavaScript)
- Backend-driven data model with SQLite persistence
- Token-based JWT authentication
- Frontend state management via Vue component composition
- External API integration (TMDB) for movie data

## Layers

**Presentation Layer (Frontend):**
- Purpose: User interface and client-side state management
- Location: `frontend/src/`
- Contains: Vue components, API client, styling
- Depends on: REST API endpoints, localStorage for token persistence
- Used by: Web browsers accessing the application

**API Layer (Backend):**
- Purpose: HTTP request handling, request validation, response formatting
- Location: `backend/main.py`
- Contains: FastAPI route definitions, Pydantic request/response models
- Depends on: Database layer, authentication module, TMDB client
- Used by: Frontend via HTTP/REST calls

**Business Logic Layer (Backend):**
- Purpose: Movie data operations, watched state management
- Location: `backend/database.py`
- Contains: CRUD functions (create_movie, get_all_movies, mark_as_watched, etc.)
- Depends on: SQLAlchemy ORM, database connection
- Used by: API layer endpoints

**Data Access Layer (Backend):**
- Purpose: Database connection and schema definition
- Location: `backend/database.py`
- Contains: SQLAlchemy Movie model definition, session management via `get_db()`
- Depends on: SQLite database file
- Used by: Business logic layer functions

**Authentication Layer (Backend):**
- Purpose: Token generation, password verification, authorization
- Location: `backend/auth.py`
- Contains: JWT token creation/validation, password verification, dependency for protected routes
- Depends on: Environment variables (SECRET_KEY, APP_PASSWORD), jose library
- Used by: API layer via `Depends(get_current_user)` dependency injection

**External Integration Layer (Backend):**
- Purpose: TMDB API communication
- Location: `backend/tmdb.py`
- Contains: Search function, movie details retrieval, image URL construction
- Depends on: TMDB API, httpx async HTTP client
- Used by: API layer `add_movie` and `search` endpoints

## Data Flow

**Movie Search Flow:**
1. User enters search query in `AddMovie` component (`frontend/src/components/AddMovie.vue`)
2. Component calls `searchMovies(query)` from `frontend/src/api.js`
3. Frontend sends GET `/api/search?q=...` with JWT token in Authorization header
4. Backend route `GET /api/search` in `backend/main.py` receives request
5. `verify_password` dependency validates token via `auth.py`
6. `search_movies(query)` function in `backend/tmdb.py` queries TMDB API asynchronously
7. Results formatted as `SearchResult` Pydantic model
8. Frontend receives JSON array of movies with tmdb_id, title, poster_url, etc.
9. User selects movie, triggering movie addition flow

**Movie Addition Flow:**
1. User selects movie from search results in `AddMovie` component
2. Component calls `addMovie(tmdbId, mediaType)` from `frontend/src/api.js`
3. Frontend sends POST `/api/movies` with `{tmdb_id, media_type}` and JWT token
4. Backend route `POST /api/movies` receives request
5. `get_current_user` validates authentication
6. `get_movie_details(tmdb_id, media_type)` fetches full details from TMDB
7. `create_movie()` in `backend/database.py` inserts record into SQLite (or returns existing)
8. Backend returns `MovieResponse` model with database id and all movie data
9. Frontend receives movie object and triggers `onMovieAdded` callback
10. App.vue calls `loadMovies()` to refresh the movies list

**Movie Watched State Flow:**
1. User clicks "Посмотрел ✓" button on unwatched movie or "watched" button in modal
2. Component emits `watched` event with movieId to parent or calls `openRatingModal()`
3. `RatingModal` component displays three impression options (liked/ok/disliked)
4. User selects impression, triggering `handleRatingSelect(impression)` in App.vue
5. App.vue calls `markAsWatched(movieId, impression)` from `frontend/src/api.js`
6. Frontend sends PATCH `/api/movies/{movieId}/watched` with impression
7. Backend route calls `mark_as_watched()` in `backend/database.py`
8. Function updates watched=true, impression, and watched_at timestamp
9. Movie is committed to database and returned as `MovieResponse`
10. Frontend updates local movies array and filters are recomputed

**State Management:**
- Frontend maintains `movies` array in `App.vue` data
- Computed properties filter movies: `toWatchMovies`, `watchedMovies`, `likedMovies`, etc.
- Active tab and filter state controlled by `activeTab` and `watchedFilter` data
- JWT token persisted in localStorage via `api.js` functions
- Backend database is single source of truth for persistent state

## Key Abstractions

**Movie Entity:**
- Purpose: Represents a film or TV show in the system
- Examples: `backend/database.py` Movie class, `frontend/src/App.vue` movie objects
- Pattern: Database model with Pydantic serialization layer; immutable in frontend until state change

**Authentication Dependency:**
- Purpose: Validate JWT tokens on protected routes
- Examples: `backend/auth.py` `get_current_user()` used as `Depends()` in FastAPI routes
- Pattern: FastAPI dependency injection; returns True if token valid, raises HTTPException 401 if not

**API Client Wrapper:**
- Purpose: Encapsulate HTTP communication and token handling
- Examples: `frontend/src/api.js` `request()` function wraps fetch() with headers and error handling
- Pattern: Centralized request builder with automatic Authorization header injection

**Component Composition:**
- Purpose: Modular UI with clear event/prop boundaries
- Examples: `App.vue` (parent container), `AddMovie.vue`, `MovieList.vue`, `MovieCard.vue`, `MovieModal.vue`, `RatingModal.vue`
- Pattern: Vue 3 single-file components with emits for child-to-parent communication

## Entry Points

**Frontend Entry Point:**
- Location: `frontend/src/main.js`
- Triggers: Browser loads the application, Vite dev server or built HTML
- Responsibilities: Creates Vue app instance, mounts to #app DOM element, initializes App.vue

**Backend Entry Point:**
- Location: `backend/main.py` (lines 203-205)
- Triggers: `uvicorn main:app` command or `python -m uvicorn main:app`
- Responsibilities: Starts FastAPI server on port 8000, initializes database via lifespan context

**Static File Serving:**
- Location: `backend/main.py` (lines 190-200)
- Triggers: Any GET request to path without `/api` prefix after frontend built
- Responsibilities: Serves built Vue app from `frontend/dist/`, fallback to index.html for SPA routing

## Error Handling

**Strategy:** Explicit exception raising with HTTP status codes

**Patterns:**
- API returns `HTTPException` with specific status codes (401 for auth, 404 for not found, 400 for validation)
- Frontend `api.js` catches non-200 responses, extracts `detail` from error JSON
- Frontend clears token on 401/403 status, redirects to login
- Frontend logs errors to console but shows minimal feedback to user

## Cross-Cutting Concerns

**Logging:** Simple console.error() on frontend; backend uses FastAPI automatic request logging

**Validation:** Pydantic models validate request bodies and serialize responses; frontend uses simple required checks

**Authentication:** JWT tokens with 30-day expiry; verified on every protected endpoint via dependency injection

---

*Architecture analysis: 2026-02-18*
