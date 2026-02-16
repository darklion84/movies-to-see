import os
import httpx
from typing import Optional

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def get_api_key() -> str:
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise ValueError("TMDB_API_KEY environment variable is not set")
    return api_key


async def search_movies(query: str, language: str = "ru-RU") -> list[dict]:
    api_key = get_api_key()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/search/movie",
            params={
                "api_key": api_key,
                "query": query,
                "language": language,
                "include_adult": False
            }
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for movie in data.get("results", [])[:10]:
            poster_path = movie.get("poster_path")
            results.append({
                "tmdb_id": movie["id"],
                "title": movie["title"],
                "description": movie.get("overview", ""),
                "poster_url": f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None,
                "rating": movie.get("vote_average", 0),
                "release_date": movie.get("release_date", "")
            })
        return results


async def get_movie_details(tmdb_id: int, language: str = "ru-RU") -> Optional[dict]:
    api_key = get_api_key()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}",
            params={
                "api_key": api_key,
                "language": language,
                "append_to_response": "credits"
            }
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        movie = response.json()

        poster_path = movie.get("poster_path")
        release_date = movie.get("release_date", "")
        release_year = int(release_date[:4]) if release_date and len(release_date) >= 4 else None

        actors = []
        credits = movie.get("credits", {})
        for cast in credits.get("cast", [])[:5]:
            actors.append(cast.get("name", ""))

        return {
            "tmdb_id": movie["id"],
            "title": movie["title"],
            "description": movie.get("overview", ""),
            "poster_url": f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None,
            "rating": movie.get("vote_average", 0),
            "release_year": release_year,
            "actors": ", ".join(actors) if actors else None
        }
