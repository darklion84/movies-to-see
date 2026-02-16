import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, Movie, create_movie, get_all_movies, delete_movie, get_movie_by_id


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_movie(test_db):
    movie = create_movie(
        test_db,
        tmdb_id=550,
        title="Fight Club",
        description="A ticking-Loss bomb of a movie",
        poster_url="https://image.tmdb.org/t/p/w500/poster.jpg",
        rating=8.4
    )
    assert movie.id is not None
    assert movie.tmdb_id == 550
    assert movie.title == "Fight Club"
    assert movie.rating == 8.4


def test_create_movie_duplicate(test_db):
    movie1 = create_movie(
        test_db,
        tmdb_id=550,
        title="Fight Club",
        description="Description",
        poster_url="https://example.com/poster.jpg",
        rating=8.4
    )
    movie2 = create_movie(
        test_db,
        tmdb_id=550,
        title="Fight Club",
        description="Description",
        poster_url="https://example.com/poster.jpg",
        rating=8.4
    )
    assert movie1.id == movie2.id


def test_get_all_movies(test_db):
    create_movie(test_db, tmdb_id=1, title="Zorro", description="", poster_url=None, rating=7.0)
    create_movie(test_db, tmdb_id=2, title="Avatar", description="", poster_url=None, rating=8.0)
    create_movie(test_db, tmdb_id=3, title="Batman", description="", poster_url=None, rating=7.5)

    movies = get_all_movies(test_db)
    assert len(movies) == 3
    assert movies[0].title == "Avatar"
    assert movies[1].title == "Batman"
    assert movies[2].title == "Zorro"


def test_delete_movie(test_db):
    movie = create_movie(
        test_db,
        tmdb_id=550,
        title="Fight Club",
        description="Description",
        poster_url="https://example.com/poster.jpg",
        rating=8.4
    )
    movie_id = movie.id

    result = delete_movie(test_db, movie_id)
    assert result is True

    deleted_movie = get_movie_by_id(test_db, movie_id)
    assert deleted_movie is None


def test_movie_not_found(test_db):
    movie = get_movie_by_id(test_db, 99999)
    assert movie is None

    result = delete_movie(test_db, 99999)
    assert result is False
