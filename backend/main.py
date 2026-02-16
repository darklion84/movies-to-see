import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from database import get_db, init_db, create_movie, get_all_movies, delete_movie, get_movie_by_id, mark_as_watched, mark_as_unwatched
from tmdb import search_movies, get_movie_details
from auth import verify_password, create_access_token, get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Movies to See", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    token: str


class AddMovieRequest(BaseModel):
    tmdb_id: int


class MovieResponse(BaseModel):
    id: int
    tmdb_id: int
    title: str
    description: str
    poster_url: str | None
    rating: float
    release_year: int | None = None
    actors: str | None = None
    watched: bool = False
    impression: str | None = None
    watched_at: datetime | None = None

    class Config:
        from_attributes = True


class WatchedRequest(BaseModel):
    impression: str | None = None


class SearchResult(BaseModel):
    tmdb_id: int
    title: str
    description: str
    poster_url: str | None
    rating: float
    release_date: str


@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    if not verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    token = create_access_token({"sub": "user"})
    return LoginResponse(token=token)


@app.get("/api/movies", response_model=list[MovieResponse])
async def get_movies(
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    movies = get_all_movies(db)
    return movies


@app.post("/api/movies", response_model=MovieResponse)
async def add_movie(
    request: AddMovieRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    movie_details = await get_movie_details(request.tmdb_id)
    if not movie_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found in TMDB"
        )

    movie = create_movie(
        db,
        tmdb_id=movie_details["tmdb_id"],
        title=movie_details["title"],
        description=movie_details["description"],
        poster_url=movie_details["poster_url"],
        rating=movie_details["rating"],
        release_year=movie_details.get("release_year"),
        actors=movie_details.get("actors")
    )
    return movie


@app.delete("/api/movies/{movie_id}")
async def remove_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    movie = get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    delete_movie(db, movie_id)
    return {"message": "Movie deleted successfully"}


@app.get("/api/search", response_model=list[SearchResult])
async def search(
    q: str,
    _: bool = Depends(get_current_user)
):
    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 2 characters"
        )
    results = await search_movies(q)
    return results


@app.patch("/api/movies/{movie_id}/watched", response_model=MovieResponse)
async def set_movie_watched(
    movie_id: int,
    request: WatchedRequest = None,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    impression = request.impression if request else None
    movie = mark_as_watched(db, movie_id, impression)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    return movie


@app.patch("/api/movies/{movie_id}/unwatched", response_model=MovieResponse)
async def set_movie_unwatched(
    movie_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    movie = mark_as_unwatched(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    return movie


# Serve frontend static files
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
