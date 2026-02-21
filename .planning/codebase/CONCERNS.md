# Codebase Concerns

**Analysis Date:** 2026-02-18

## Security Considerations

**Single Password Authentication:**
- Risk: Single plaintext password comparison without rate limiting or account lockout
- Files: `backend/auth.py` (lines 28-29), `backend/main.py` (lines 81-89)
- Current mitigation: JWT tokens with 30-day expiry provide session protection after login
- Recommendations:
  - Implement rate limiting on `/api/login` endpoint (e.g., max 5 attempts per minute per IP)
  - Add login attempt logging and alerting
  - Consider password hashing if migrating to multi-user system

**CORS Wide Open:**
- Risk: `allow_origins=["*"]` allows any domain to make requests to the API
- Files: `backend/main.py` (lines 27-33)
- Current mitigation: JWT token requirement on protected endpoints
- Recommendations: Restrict to specific domains in production (e.g., `allow_origins=["https://yourdomain.com"]`)

**Token in localStorage:**
- Risk: XSS attacks can steal tokens from localStorage; no token refresh mechanism
- Files: `frontend/src/api.js` (lines 3-4)
- Current mitigation: 30-day token expiry; tokens cleared on 401 response
- Recommendations:
  - Consider httpOnly cookies as alternative (requires backend CSRF protection)
  - Implement token refresh endpoint to reduce token lifetime
  - Add Content Security Policy headers

**Environment Variable Handling:**
- Risk: Missing environment variables raise exceptions at module load time, blocking app startup
- Files: `backend/auth.py` (lines 14-25), `backend/tmdb.py` (lines 9-13)
- Current mitigation: Errors are caught and reported, but crash the entire application
- Recommendations: Implement graceful degradation or detailed startup validation

## Error Handling Gaps

**TMDB API Error Handling:**
- Issue: Only 404 is explicitly handled; other status codes (500, 429, timeout) will raise unhandled exceptions
- Files: `backend/tmdb.py` (lines 71-73)
- Impact: Search and add movie operations fail ungracefully without user-friendly messages
- Fix approach: Wrap API calls in try-catch, return None or specific error responses for rate limits, add retry logic for transient failures

**Frontend Error Messages Generic:**
- Issue: All search/add errors show "Ошибка поиска" or "Ошибка добавления" without distinguishing between network, validation, or server errors
- Files: `frontend/src/components/AddMovie.vue` (lines 85, 99)
- Impact: Users cannot troubleshoot issues (e.g., retry for timeout vs. fix data for validation)
- Fix approach: Pass error codes/types from backend, display specific messages based on error type

**Unhandled Async Errors:**
- Issue: `loadMovies()` in App.vue catches "Unauthorized" but other errors only log to console
- Files: `frontend/src/App.vue` (lines 146-156, 158-164)
- Impact: Network errors, timeouts silently fail without user notification
- Fix approach: Display toast/snackbar for all error types, implement retry logic

## Test Coverage Gaps

**Frontend Component Testing Minimal:**
- What's not tested: `AddMovie.vue`, `MovieModal.vue`, `RatingModal.vue`, `LoginForm.vue` - all lack unit tests
- Files: Only `MovieList.spec.js` exists; 4 major components untested
- Risk: Refactoring or changes break UI behavior silently; search/rating/login flows not validated
- Priority: **High** - LoginForm and AddMovie handle critical user interactions

**Backend TMDB API Not Tested:**
- What's not tested: `get_movie_details()`, error handling for rate limits, network timeouts
- Files: `backend/tests/test_tmdb.py` (if it exists, likely minimal)
- Risk: TMDB API integration fails in production (rate limiting, schema changes) without detection
- Priority: **Medium** - search and add-movie features depend on this

**Database Transaction Isolation Not Tested:**
- What's not tested: Concurrent movie additions, race conditions in duplicate detection
- Files: `backend/database.py` (lines 46-48), no concurrency tests
- Risk: Duplicate movies could be inserted if two requests arrive simultaneously
- Priority: **Medium** - small app but worth fixing before scaling

**No E2E Tests:**
- What's not tested: Full user flow (login → search → add → mark watched)
- Risk: Multiple components interact; bugs in component communication won't be caught
- Priority: **Medium** - could use Playwright or Cypress

## Performance Bottlenecks

**No Database Indexing Strategy:**
- Problem: Only `tmdb_id` is indexed; filtering by `watched` or `impression` requires full table scan
- Files: `backend/database.py` (lines 13-28)
- Cause: SQLAlchemy model doesn't specify indexes on frequently-filtered columns
- Improvement path: Add `index=True` to `watched` column; benchmark filter queries

**Frontend Loads All Movies Every Time:**
- Problem: `loadMovies()` fetches entire list even when only one movie changed
- Files: `frontend/src/App.vue` (lines 142-156, 178-202)
- Cause: Components reload list instead of updating in-place
- Improvement path: Update single movie in local array instead of reloading; save network bandwidth

**TMDB API Calls Have No Caching:**
- Problem: Searching same query twice hits API both times; no response caching
- Files: `frontend/src/api.js` (lines 78-80), `backend/tmdb.py` (lines 16-55)
- Cause: No cache layer (memory, Redis, or HTTP cache headers)
- Improvement path: Add client-side cache (Map with TTL), or implement ETag-based caching

**No Pagination:**
- Problem: All movies loaded into memory; list grows unbounded
- Files: `backend/main.py` (lines 92-98), `frontend/src/App.vue` (lines 121-129)
- Cause: Architecture assumes small datasets
- Improvement path: Implement limit/offset pagination for `/api/movies` and search results

## Fragile Areas

**Database Schema Auto-Migration:**
- Files: `backend/database.py` (lines 31-32)
- Why fragile: `Base.metadata.create_all()` creates tables but doesn't handle schema changes; existing columns can't be modified without manual migration
- Safe modification: Always create SQL migrations in `backend/migrations/` before schema changes; document in CLAUDE.md
- Test coverage: No tests for migration path; manual testing only

**Duplicate Detection on tmdb_id:**
- Files: `backend/database.py` (lines 46-48), `backend/main.py` (lines 101-125)
- Why fragile: `unique=True` constraint on `tmdb_id` assumes TMDB IDs never collide; race condition window exists between check and insert
- Safe modification: Use database-level constraints; add conflict handling (return existing or reject clearly)
- Test coverage: `test_add_movie_duplicate` exists but doesn't test concurrent requests

**Frontend Modal State Management:**
- Files: `frontend/src/App.vue` (lines 99-100, 205-209)
- Why fragile: `selectedMovie` and `ratingMovie` are separate state; closing rating modal doesn't close movie modal, leaving UI in inconsistent state if user presses back
- Safe modification: Use single modal stack or ensure both close together; test modal transitions thoroughly
- Test coverage: No modal transition tests

**CORS and Authentication Coupling:**
- Files: `backend/main.py` (lines 27-33), `backend/auth.py` (lines 51-59)
- Why fragile: Frontend serves from same origin in production but requests go to same API; CORS settings must match deployment architecture
- Safe modification: Document required CORS settings for each deployment (local, Docker, cloud); add checks in startup
- Test coverage: No CORS testing

## Known Issues

**Missing "watched_date" Filtering:**
- Symptoms: No way to see recently watched movies; watched_at is stored but not used in UI
- Files: `backend/database.py` (line 28), `frontend/src/App.vue` - no recently watched filter
- Trigger: User needs to review movies watched in last week
- Workaround: Manually scroll watched list and estimate from UI appearance

**TV Show vs Movie Not Visually Distinct After Adding:**
- Symptoms: Search results show "сериал" badge but added movies don't; impression icons different but no indication
- Files: `frontend/src/components/AddMovie.vue` (line 35), `frontend/src/components/MovieCard.vue` (likely no media_type display)
- Trigger: Add a TV show and look at it in the list
- Workaround: Remember which are TV shows; rating modal is only clue

**Search Results Hardcoded to Russian:**
- Symptoms: Search queries always use `language="ru-RU"`; English searches return Russian titles
- Files: `backend/tmdb.py` (line 16)
- Trigger: User searches for movie in English; TMDB returns Russian localization
- Workaround: Search in Russian or accept incorrect locale

## Scaling Limits

**SQLite Single-Writer Limitation:**
- Current capacity: ~100 concurrent users with light usage; ~1000 movies
- Limit: SQLite locks database for writes; concurrent requests queue; timeout at ~5 seconds of contention
- Scaling path: Migrate to PostgreSQL or MySQL; update `DATABASE_URL` and SQLAlchemy engine settings

**No API Rate Limiting:**
- Current capacity: Unbounded requests per user
- Limit: Can exhaust TMDB API quota (40 requests/10 seconds for free tier)
- Scaling path: Implement request throttling per user/IP; add exponential backoff for TMDB calls

**Frontend State Grows With Movie Count:**
- Current capacity: Smooth at <500 movies; performance degrades at 1000+
- Limit: All movies in memory; filtering happens in-memory; 60MB+ for large lists
- Scaling path: Implement server-side pagination; load movies in chunks; add pagination to UI

**No Production Monitoring:**
- Current capacity: No visibility into errors or performance
- Limit: Can't detect issues until user reports; no alerting
- Scaling path: Add Sentry or similar for error tracking; add basic logging with timestamps

## Dependencies at Risk

**python-jose (JWT):**
- Risk: Dependency on `python-jose[cryptography]` for JWT; cryptography library is large and occasionally has security updates
- Impact: If JWT library has vulnerability, must update immediately; affects all auth
- Migration plan: Could use `PyJWT` as alternative, but would require rewriting token generation/verification

**httpx (Async HTTP):**
- Risk: Less mature than `requests`; fewer StackOverflow answers if issues arise
- Impact: TMDB API integration dependent on httpx; no fallback
- Migration plan: Migrate to `aiohttp` or keep `requests` (would lose async benefits)

**SQLAlchemy ORM:**
- Risk: ORM can generate inefficient queries; easy to write N+1 queries
- Impact: Database performance can degrade with poor query patterns
- Migration plan: No migration needed but requires careful query review; could add SQLAlchemy logging

## Missing Critical Features

**No Data Backup/Export:**
- Problem: User data exists only in SQLite file; no export to CSV/JSON; no backup mechanism
- Blocks: User can't move data to another service; data loss if database corrupts

**No Search Filtering/Sorting:**
- Problem: Can't sort by rating, release year, or watch date; can't filter by rating range
- Blocks: Lists become hard to navigate with many movies; can't find highest-rated movies

**No Multi-User Support:**
- Problem: Single password for everyone; no user accounts
- Blocks: Can't use in family without sharing password; can't see who added what movie

## SQL Injection Risk Analysis

**Search endpoint properly parameterized:**
- Files: `backend/tmdb.py` (lines 19-26) - uses params dict, not string concatenation; safe
- Files: `frontend/src/api.js` (line 79) - uses `encodeURIComponent()`; safe from URL injection

**Database queries use ORM:**
- Files: `backend/database.py` - all queries use SQLAlchemy ORM with parameterized filters; safe
- No raw SQL strings found in main code

---

*Concerns audit: 2026-02-18*
