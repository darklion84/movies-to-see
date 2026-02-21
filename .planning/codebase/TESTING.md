# Testing Patterns

**Analysis Date:** 2026-02-18

## Test Framework

**Backend Runner:**
- pytest [8.0.0+]
- Config: No explicit config file; default pytest discovery
- Command: `cd backend && pytest -v`
- Single test: `pytest tests/test_api.py::test_login -v`

**Frontend Runner:**
- vitest [1.2.1+] (Vite native test runner)
- Config: `frontend/vite.config.js` (test environment set to jsdom)
- Command: `cd frontend && npm test`

**Assertion Library:**
- Backend: pytest assertions
- Frontend: vitest expect API

**Run Commands:**
```bash
# Backend: all tests
cd backend && pytest -v

# Backend: single test
pytest tests/test_api.py::test_login -v

# Backend: with asyncio support
pytest -v  # asyncio auto-used via pytest-asyncio fixture

# Frontend: all tests
cd frontend && npm test

# Frontend: watch mode
cd frontend && npm test -- --watch
```

## Test File Organization

**Location Pattern:**
- Backend: `backend/tests/` directory
- Frontend: `frontend/src/components/__tests__/` directory (co-located with components)

**Naming Convention:**
- Backend: `test_<module>.py` (e.g., `test_api.py`, `test_database.py`, `test_tmdb.py`)
- Frontend: `<ComponentName>.spec.js` (e.g., `MovieList.spec.js`)

**Directory Structure:**
```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_api.py          # API endpoint tests
│   ├── test_database.py     # Database CRUD tests
│   └── test_tmdb.py         # TMDB client tests

frontend/
├── src/
│   └── components/
│       ├── MovieList.vue
│       ├── MovieCard.vue
│       └── __tests__/
│           └── MovieList.spec.js
```

## Test Structure

**Backend Suite Organization (from `test_api.py`):**

```python
import pytest
from unittest.mock import patch, AsyncMock


def test_login_success(client):
    response = client.post("/api/login", json={"password": "test_password"})
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_failure(client):
    response = client.post("/api/login", json={"password": "wrong_password"})
    assert response.status_code == 401
```

**Patterns:**
- Test functions named `test_<scenario>` (verb + condition)
- Descriptive names indicate test purpose: `test_login_success`, `test_add_movie`, `test_delete_nonexistent_movie`
- Minimal setup within test function (setup delegated to fixtures)
- Arrange-Act-Assert pattern implicit in structure:
  - Arrange: Use fixture data
  - Act: Call endpoint/function
  - Assert: Check response/return value

**Frontend Suite Organization (from `MovieList.spec.js`):**

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MovieList from '../MovieList.vue'

describe('MovieList', () => {
  it('renders empty state when no movies', () => {
    const wrapper = mount(MovieList, {
      props: { movies: [] }
    })
    expect(wrapper.text()).toContain('Список пуст')
  })

  it('renders movie cards for each movie', () => {
    const movies = [
      { id: 1, tmdb_id: 100, title: 'Movie 1', poster_url: null, rating: 7.5 }
    ]
    const wrapper = mount(MovieList, {
      props: { movies },
      global: {
        components: { MovieCard }
      }
    })
    const cards = wrapper.findAllComponents(MovieCard)
    expect(cards.length).toBe(2)
  })
})
```

**Patterns:**
- `describe()` groups related tests
- `it()` names scenarios as assertions: "renders empty state when no movies"
- Mount component with props/global options
- Assert using `expect()` API with methods like `.toContain()`, `.toBe()`, `.toBeTruthy()`
- Component instance accessed via `wrapper` variable

## Mocking

**Framework:** `unittest.mock` (backend), `vitest` built-in mocking (frontend)

**Async Mocking Pattern (from `test_api.py`):**

```python
from unittest.mock import patch, AsyncMock

def test_add_movie(client, auth_headers):
    mock_movie_details = {
        "tmdb_id": 157336,
        "title": "Интерстеллар",
        "description": "Фильм о космосе",
        "poster_url": "https://image.tmdb.org/t/p/w500/poster.jpg",
        "rating": 8.6
    }

    with patch("main.get_movie_details", new_callable=AsyncMock) as mock:
        mock.return_value = mock_movie_details
        response = client.post(
            "/api/movies",
            json={"tmdb_id": 157336},
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Интерстеллар"
```

**HTTP Client Mocking (from `test_tmdb.py`):**

```python
@pytest.fixture
def httpx_mock():
    """Custom httpx mock fixture for TMDB API testing"""
    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self._json_data = json_data
            self.status_code = status_code

        def json(self):
            return self._json_data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise httpx.HTTPStatusError("Error", request=None, response=self)

    class HttpxMock:
        def __init__(self):
            self.responses = {}

        def add_response(self, method, path, json, status_code=200):
            key = f"{method}:{path}"
            self.responses[key] = MockResponse(json, status_code)

        async def get(self, url, params=None):
            parsed = urlparse(url)
            key = f"GET:{parsed.path}"
            if key in self.responses:
                return self.responses[key]
            raise Exception(f"No mock for: {key}")

    mock = HttpxMock()

    class MockClient:
        async def __aenter__(self):
            return mock
        async def __aexit__(self, *args):
            pass

    with patch("httpx.AsyncClient", MockClient):
        yield mock
```

**What to Mock:**
- External API calls (TMDB API via `httpx.AsyncClient`)
- Functions that depend on external services
- Database operations (via fixture override in conftest)

**What NOT to Mock:**
- Database layer in integration tests (use test database fixture)
- Core business logic (CRUD operations, validation)
- Component props and event emissions in Vue tests

## Fixtures and Factories

**Backend Fixtures (from `conftest.py`):**

```python
@pytest.fixture(scope="function")
def client():
    """Creates test client with isolated database"""
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    test_db_url = f"sqlite:///{db_path}"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    from database import Base, get_db
    Base.metadata.create_all(bind=engine)

    from main import app

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    os.unlink(db_path)


@pytest.fixture
def auth_headers(client):
    """Provides authenticated headers for protected endpoints"""
    response = client.post("/api/login", json={"password": "test_password"})
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
```

**Database Fixture (from `test_database.py`):**

```python
@pytest.fixture
def test_db():
    """Creates in-memory SQLite database for unit tests"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Environment Setup (from `conftest.py`):**

```python
import os
import sys

os.environ["APP_PASSWORD"] = "test_password"
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["TMDB_API_KEY"] = "test_tmdb_key"
```

**Frontend Fixture (from `MovieList.spec.js`):**

```javascript
const movies = [
    { id: 1, tmdb_id: 100, title: 'Movie 1', poster_url: null, rating: 7.5 },
    { id: 2, tmdb_id: 101, title: 'Movie 2', poster_url: null, rating: 8.0 }
]

const wrapper = mount(MovieList, {
    props: { movies },
    global: {
        components: { MovieCard }
    }
})
```

**Test Data Location:**
- Backend: Inline in test functions or fixtures
- Frontend: Inline in test functions as JS objects
- No separate fixture files or factories

## Coverage

**Requirements:** Not enforced

**Current State:**
- Backend tests cover: API endpoints, database operations, TMDB client
- Frontend tests cover: Component rendering, event emission

**Test Files:**
- `backend/tests/test_api.py` - 7 tests for API routes
- `backend/tests/test_database.py` - 5 tests for CRUD operations
- `backend/tests/test_tmdb.py` - 5 tests for TMDB client
- `frontend/src/components/__tests__/MovieList.spec.js` - 3 tests for list component

## Test Types

**Unit Tests:**
- **Database tests** (`test_database.py`):
  - Test individual CRUD functions in isolation
  - Use in-memory SQLite database
  - Scope: Single function behavior

- **TMDB client tests** (`test_tmdb.py`):
  - Test search and detail API functions
  - Use custom HTTP mocking
  - Scope: API response parsing and formatting

**Integration Tests:**
- **API tests** (`test_api.py`):
  - Test complete request-response cycle
  - Include authentication, database, and mocked external APIs
  - Scope: Endpoint behavior with dependencies

**Component Tests:**
- **Vue component tests** (`MovieList.spec.js`):
  - Test component rendering with props
  - Test event emission
  - Scope: Single component behavior

**E2E Tests:**
- Not used in this codebase

## Common Patterns

**Async Testing:**

```python
@pytest.mark.asyncio
async def test_search_movie(mock_env, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        path="/3/search/multi",
        json={
            "results": [
                {
                    "id": 157336,
                    "media_type": "movie",
                    "title": "Интерстеллар",
                    "overview": "Фильм о космосе",
                    "poster_path": "/poster.jpg",
                    "vote_average": 8.6,
                    "release_date": "2014-11-05"
                }
            ]
        }
    )

    results = await search_movies("Interstellar")
    assert len(results) == 1
    assert results[0]["tmdb_id"] == 157336
```

**Pattern:**
- `@pytest.mark.asyncio` decorator enables async test functions
- Mock HTTP response before calling async function
- Assert on returned data structure

**Error Testing:**

```python
def test_login_failure(client):
    response = client.post("/api/login", json={"password": "wrong_password"})
    assert response.status_code == 401
```

**Pattern:**
- Call function/endpoint with invalid data
- Assert HTTP status code or exception type
- Verify error message if applicable

**Duplicate/Idempotency Testing:**

```python
def test_add_movie_duplicate(client, auth_headers):
    mock_movie_details = {
        "tmdb_id": 157336,
        "title": "Интерстеллар",
        "description": "Фильм о космосе",
        "poster_url": "https://image.tmdb.org/t/p/w500/poster.jpg",
        "rating": 8.6
    }

    with patch("main.get_movie_details", new_callable=AsyncMock) as mock:
        mock.return_value = mock_movie_details
        response1 = client.post("/api/movies", json={"tmdb_id": 157336}, headers=auth_headers)
        response2 = client.post("/api/movies", json={"tmdb_id": 157336}, headers=auth_headers)

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()["id"] == response2.json()["id"]
```

**Pattern:**
- Perform same operation twice
- Verify both succeed
- Verify idempotency (same result)

**Event Emission Testing (Vue):**

```javascript
it('emits delete event when movie card emits delete', async () => {
    const movies = [
        { id: 1, tmdb_id: 100, title: 'Movie 1', poster_url: null, rating: 7.5 }
    ]
    const wrapper = mount(MovieList, {
        props: { movies },
        global: { components: { MovieCard } }
    })
    const card = wrapper.findComponent(MovieCard)
    await card.vm.$emit('delete', 1)
    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')[0]).toEqual([1])
})
```

**Pattern:**
- Mount parent component with child component
- Emit event from child via `$emit()`
- Assert parent received event via `wrapper.emitted()`
- Verify event payload matches expected data

---

*Testing analysis: 2026-02-18*
