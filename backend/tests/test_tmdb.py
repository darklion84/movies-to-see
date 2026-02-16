import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tmdb import search_movies, get_movie_details


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("TMDB_API_KEY", "test_api_key")


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
    assert results[0]["title"] == "Интерстеллар"
    assert results[0]["rating"] == 8.6
    assert results[0]["media_type"] == "movie"


@pytest.mark.asyncio
async def test_search_tv_show(mock_env, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        path="/3/search/multi",
        json={
            "results": [
                {
                    "id": 94997,
                    "media_type": "tv",
                    "name": "Дом Дракона",
                    "overview": "Сериал о Таргариенах",
                    "poster_path": "/poster.jpg",
                    "vote_average": 8.4,
                    "first_air_date": "2022-08-21"
                }
            ]
        }
    )

    results = await search_movies("House of the Dragon")
    assert len(results) == 1
    assert results[0]["title"] == "Дом Дракона"
    assert results[0]["media_type"] == "tv"
    assert results[0]["release_date"] == "2022-08-21"


@pytest.mark.asyncio
async def test_get_movie_details(mock_env, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        path="/3/movie/157336",
        json={
            "id": 157336,
            "title": "Интерстеллар",
            "overview": "Фильм о космосе",
            "poster_path": "/poster.jpg",
            "vote_average": 8.6
        }
    )

    result = await get_movie_details(157336, "movie")
    assert result is not None
    assert result["tmdb_id"] == 157336
    assert result["poster_url"] == "https://image.tmdb.org/t/p/w500/poster.jpg"
    assert result["media_type"] == "movie"


@pytest.mark.asyncio
async def test_get_tv_details(mock_env, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        path="/3/tv/94997",
        json={
            "id": 94997,
            "name": "Дом Дракона",
            "overview": "Сериал о Таргариенах",
            "poster_path": "/poster.jpg",
            "vote_average": 8.4,
            "first_air_date": "2022-08-21"
        }
    )

    result = await get_movie_details(94997, "tv")
    assert result is not None
    assert result["tmdb_id"] == 94997
    assert result["title"] == "Дом Дракона"
    assert result["media_type"] == "tv"


@pytest.mark.asyncio
async def test_search_no_results(mock_env, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        path="/3/search/multi",
        json={"results": []}
    )

    results = await search_movies("xyznonexistent123")
    assert len(results) == 0


@pytest.fixture
def httpx_mock():
    import httpx
    from unittest.mock import patch
    from urllib.parse import urlparse

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
        def __init__(self):
            pass

        async def __aenter__(self):
            return mock

        async def __aexit__(self, *args):
            pass

    with patch("httpx.AsyncClient", MockClient):
        yield mock
