# Coding Conventions

**Analysis Date:** 2026-02-18

## Naming Patterns

**Files:**
- Python files: lowercase with underscores (`auth.py`, `tmdb.py`, `database.py`)
- Vue components: PascalCase with `.vue` extension (`LoginForm.vue`, `MovieCard.vue`, `AddMovie.vue`)
- JavaScript modules: camelCase with `.js` extension (`api.js`, `main.js`)
- Test files: snake_case prefixed with `test_` (`test_api.py`, `test_database.py`)
- Test Vue components: snake_case with `.spec.js` suffix (`MovieList.spec.js`)

**Functions:**
- Python: lowercase with underscores (`create_movie`, `get_all_movies`, `mark_as_watched`)
- JavaScript: camelCase (`getToken`, `setToken`, `isAuthenticated`, `handleLogin`, `debouncedSearch`)
- Vue methods: camelCase (`openModal`, `closeModal`, `handleRatingSelect`)

**Variables:**
- Python: lowercase with underscores (`movie_id`, `session_local`, `tmdb_id`)
- JavaScript/Vue: camelCase (`query`, `results`, `loading`, `selectedMovie`, `activeTab`)
- Class attributes: camelCase in Vue components (`poster_url`, `watched_at`, `impression`)

**Types & Classes:**
- Python SQLAlchemy models: PascalCase (`Movie`)
- Pydantic models: PascalCase (`LoginRequest`, `MovieResponse`, `AddMovieRequest`, `WatchedRequest`, `SearchResult`)
- Vue component names: PascalCase (`LoginForm`, `MovieCard`, `MovieModal`, `RatingModal`)

**Constants:**
- Python: SCREAMING_SNAKE_CASE (`TMDB_BASE_URL`, `TMDB_IMAGE_BASE_URL`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_DAYS`, `DATABASE_URL`)
- JavaScript: SCREAMING_SNAKE_CASE for base URLs (`API_BASE`)

## Code Style

**Formatting:**
- No explicit formatter configured (no `.eslintrc`, `.prettierrc`, or Prettier config)
- Python uses standard PEP 8 conventions (4-space indentation)
- JavaScript/Vue uses standard JavaScript conventions (2-space indentation visible in package files)
- Vue components use scoped styles with consistent formatting

**Linting:**
- No explicit linter configured for Python or JavaScript
- Code follows implicit patterns observed in existing modules

**Indentation:**
- Python: 4 spaces (standard PEP 8)
- JavaScript/Vue: 2 spaces (standard Vue/Vite convention)

## Import Organization

**Python Order:**
1. Standard library imports (`os`, `datetime`, `tempfile`, `sys`)
2. Third-party framework imports (`fastapi`, `sqlalchemy`, `pytest`)
3. Third-party utilities (`httpx`, `python-jose`, `dotenv`)
4. Local module imports (`.database`, `.auth`, `.tmdb`)

**Example (from `main.py`):**
```python
import os
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, init_db, create_movie
from tmdb import search_movies, get_movie_details
from auth import verify_password, create_access_token, get_current_user
```

**JavaScript/Vue Order:**
1. Framework imports (`@vitejs/plugin-vue`, `vue`, `@vue/test-utils`)
2. Local module imports (`./api.js`, `./components/*`)
3. Component imports listed in dependency order

**Example (from `AddMovie.vue`):**
```javascript
import { searchMovies, addMovie } from '../api.js'
```

**Example (from `App.vue`):**
```javascript
import LoginForm from './components/LoginForm.vue'
import AddMovie from './components/AddMovie.vue'
import MovieList from './components/MovieList.vue'
import { getMovies, deleteMovie, markAsWatched } from './api.js'
```

## Error Handling

**Python Patterns:**
- HTTPException for API errors with appropriate status codes
- Environment variable validation in getter functions that raise `ValueError`
- Try-finally pattern for resource cleanup (database connections)

**Example (from `auth.py`):**
```python
def get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("SECRET_KEY environment variable is not set")
    return secret_key
```

**Example (from `database.py`):**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**JavaScript/Vue Patterns:**
- Try-catch-finally for async operations
- Store errors in component data property (`error` field)
- Display errors to user through template conditionals
- Clear errors before new operations

**Example (from `api.js`):**
```javascript
if (response.status === 401 || response.status === 403) {
    clearToken()
    throw new Error('Unauthorized')
}

if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || 'Request failed')
}
```

**Example (from `AddMovie.vue`):**
```javascript
async search() {
    this.searching = true
    this.error = ''

    try {
        this.results = await searchMovies(this.query)
    } catch (e) {
        this.error = 'Ошибка поиска'
    } finally {
        this.searching = false
    }
}
```

## Logging

**Framework:** `console` (JavaScript/Vue) and implicit FastAPI logging

**Patterns:**
- Python: Implicit logging through FastAPI request/response
- JavaScript: `console.error()` for error logging in catch blocks

**Example (from `App.vue`):**
```javascript
catch (e) {
    console.error('Failed to delete movie', e)
}
```

**When to Log:**
- Error scenarios where exception is caught but handled gracefully
- Critical failures in async operations

## Comments

**When to Comment:**
- Comments are minimal and reserved for non-obvious logic
- Inline comments explain TMDB API field mapping (movie vs. TV show differences)

**Example (from `tmdb.py`):**
```python
# TV shows use 'name' and 'first_air_date', movies use 'title' and 'release_date'
title = item.get("title") or item.get("name", "")
release_date = item.get("release_date") or item.get("first_air_date", "")
```

**JSDoc/TSDoc:**
- Not used in this codebase
- Type hints used implicitly through Python type annotations and Vue prop definitions

## Function Design

**Size Guidelines:**
- Small, focused functions (10-30 lines typical)
- Database functions in `database.py` are single-responsibility (create, read, update, delete operations)
- API route handlers delegate to imported functions (`database`, `auth`, `tmdb`)

**Parameters:**
- Python functions accept `db: Session` parameter for database operations
- API endpoints use FastAPI `Depends()` for dependency injection
- Vue methods use `this` for component state access

**Return Values:**
- Python database functions return ORM models or None
- Python API endpoints return Pydantic response models
- JavaScript/Vue async functions return API response data
- Boolean returns for operations that succeed/fail (delete_movie, verify_token)

**Example (from `database.py`):**
```python
def create_movie(db, tmdb_id: int, title: str, description: str, poster_url: str,
                 rating: float, release_year: int = None, actors: str = None,
                 media_type: str = "movie"):
    existing = db.query(Movie).filter(Movie.tmdb_id == tmdb_id).first()
    if existing:
        return existing

    movie = Movie(...)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie
```

## Module Design

**Exports:**
- Python: Functions imported by name in main.py
- JavaScript: Named exports in `api.js` with barrel pattern

**Example (from `api.js`):**
```javascript
export {
    login,
    logout,
    getMovies,
    addMovie,
    deleteMovie,
    searchMovies,
    markAsWatched,
    markAsUnwatched,
    isAuthenticated,
    clearToken
}
```

**Barrel Files:**
- Vue components are imported individually (no index.js barrel files)
- Each component file is self-contained

**Module Responsibility:**
- `auth.py`: JWT token creation/verification, password validation
- `database.py`: SQLAlchemy model definition and CRUD operations
- `tmdb.py`: TMDB API client with search and details endpoints
- `main.py`: FastAPI routes and Pydantic models
- `api.js`: HTTP client wrapper with token management
- Component files: Single Vue component per file

## Vue Component Conventions

**Template Structure:**
- Root element uses semantic class names (`.app`, `.movie-card`, `.login-container`)
- Event handlers use `@` directive syntax
- Conditionals use `v-if`, `v-else` for major branches
- Lists use `v-for` with `:key` binding

**Script Structure:**
- `name` field always specified for debugging
- `data()` returns object with component state
- `computed` properties for derived state
- `methods` for event handlers and user actions
- `mounted()` for initialization logic
- `props` with type validation
- `emits` array declares output events

**Style Structure:**
- `<style scoped>` used in all components for style isolation
- CSS classes use kebab-case (`.movie-card`, `.empty-state`, `.result-item`)
- Color scheme uses dark theme variables: `#0f0f23`, `#1a1a2e`, `#333`, `#e94560`, `#888`

---

*Convention analysis: 2026-02-18*
