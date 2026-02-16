from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./movies.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    poster_url = Column(String)
    rating = Column(Float)
    release_year = Column(Integer, nullable=True)
    actors = Column(String, nullable=True)
    watched = Column(Boolean, default=False)
    impression = Column(String, nullable=True)  # liked, ok, disliked
    added_at = Column(DateTime, default=datetime.utcnow)
    watched_at = Column(DateTime, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_movie(db, tmdb_id: int, title: str, description: str, poster_url: str,
                 rating: float, release_year: int = None, actors: str = None):
    existing = db.query(Movie).filter(Movie.tmdb_id == tmdb_id).first()
    if existing:
        return existing

    movie = Movie(
        tmdb_id=tmdb_id,
        title=title,
        description=description,
        poster_url=poster_url,
        rating=rating,
        release_year=release_year,
        actors=actors
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def get_all_movies(db):
    return db.query(Movie).order_by(Movie.title).all()


def get_movie_by_id(db, movie_id: int):
    return db.query(Movie).filter(Movie.id == movie_id).first()


def delete_movie(db, movie_id: int):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        db.delete(movie)
        db.commit()
        return True
    return False


def mark_as_watched(db, movie_id: int, impression: str = None):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        movie.watched = True
        movie.impression = impression
        movie.watched_at = datetime.utcnow()
        db.commit()
        db.refresh(movie)
        return movie
    return None


def mark_as_unwatched(db, movie_id: int):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        movie.watched = False
        movie.impression = None
        movie.watched_at = None
        db.commit()
        db.refresh(movie)
        return movie
    return None
