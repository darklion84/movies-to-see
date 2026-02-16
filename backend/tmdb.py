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
            f"{TMDB_BASE_URL}/search/multi",
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
        for item in data.get("results", []):
            media_type = item.get("media_type")
            if media_type not in ("movie", "tv"):
                continue

            poster_path = item.get("poster_path")
            # TV shows use 'name' and 'first_air_date', movies use 'title' and 'release_date'
            title = item.get("title") or item.get("name", "")
            release_date = item.get("release_date") or item.get("first_air_date", "")

            results.append({
                "tmdb_id": item["id"],
                "title": title,
                "description": item.get("overview", ""),
                "poster_url": f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None,
                "rating": item.get("vote_average", 0),
                "release_date": release_date,
                "media_type": media_type
            })

            if len(results) >= 10:
                break

        return results


async def get_movie_details(tmdb_id: int, media_type: str = "movie", language: str = "ru-RU") -> Optional[dict]:
    api_key = get_api_key()
    endpoint = "movie" if media_type == "movie" else "tv"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TMDB_BASE_URL}/{endpoint}/{tmdb_id}",
            params={
                "api_key": api_key,
                "language": language,
                "append_to_response": "credits"
            }
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        item = response.json()

        poster_path = item.get("poster_path")

        # TV shows use 'name' and 'first_air_date', movies use 'title' and 'release_date'
        title = item.get("title") or item.get("name", "")
        release_date = item.get("release_date") or item.get("first_air_date", "")
        release_year = int(release_date[:4]) if release_date and len(release_date) >= 4 else None

        actors = []
        credits = item.get("credits", {})
        for cast in credits.get("cast", [])[:5]:
            actors.append(cast.get("name", ""))

        return {
            "tmdb_id": item["id"],
            "title": title,
            "description": item.get("overview", ""),
            "poster_url": f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None,
            "rating": item.get("vote_average", 0),
            "release_year": release_year,
            "actors": ", ".join(actors) if actors else None,
            "media_type": media_type
        }
