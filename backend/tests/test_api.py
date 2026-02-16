import pytest
from unittest.mock import patch, AsyncMock


def test_login_success(client):
    response = client.post("/api/login", json={"password": "test_password"})
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_failure(client):
    response = client.post("/api/login", json={"password": "wrong_password"})
    assert response.status_code == 401


def test_get_movies_unauthorized(client):
    response = client.get("/api/movies")
    assert response.status_code == 401


def test_get_movies_empty(client, auth_headers):
    response = client.get("/api/movies", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


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
    assert data["tmdb_id"] == 157336


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


def test_delete_movie(client, auth_headers):
    mock_movie_details = {
        "tmdb_id": 157336,
        "title": "Интерстеллар",
        "description": "Фильм о космосе",
        "poster_url": "https://image.tmdb.org/t/p/w500/poster.jpg",
        "rating": 8.6
    }

    with patch("main.get_movie_details", new_callable=AsyncMock) as mock:
        mock.return_value = mock_movie_details
        add_response = client.post("/api/movies", json={"tmdb_id": 157336}, headers=auth_headers)

    movie_id = add_response.json()["id"]
    delete_response = client.delete(f"/api/movies/{movie_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    movies_response = client.get("/api/movies", headers=auth_headers)
    assert len(movies_response.json()) == 0


def test_movies_sorted_alphabetically(client, auth_headers):
    movies = [
        {"tmdb_id": 1, "title": "Zorro", "description": "", "poster_url": None, "rating": 7.0},
        {"tmdb_id": 2, "title": "Avatar", "description": "", "poster_url": None, "rating": 8.0},
        {"tmdb_id": 3, "title": "Batman", "description": "", "poster_url": None, "rating": 7.5}
    ]

    with patch("main.get_movie_details", new_callable=AsyncMock) as mock:
        for movie in movies:
            mock.return_value = movie
            client.post("/api/movies", json={"tmdb_id": movie["tmdb_id"]}, headers=auth_headers)

    response = client.get("/api/movies", headers=auth_headers)
    data = response.json()

    assert len(data) == 3
    assert data[0]["title"] == "Avatar"
    assert data[1]["title"] == "Batman"
    assert data[2]["title"] == "Zorro"


def test_search_movies(client, auth_headers):
    mock_results = [
        {
            "tmdb_id": 157336,
            "title": "Интерстеллар",
            "description": "Фильм о космосе",
            "poster_url": "https://image.tmdb.org/t/p/w500/poster.jpg",
            "rating": 8.6,
            "release_date": "2014-11-05"
        }
    ]

    with patch("main.search_movies", new_callable=AsyncMock) as mock:
        mock.return_value = mock_results
        response = client.get("/api/search?q=Interstellar", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Интерстеллар"


def test_delete_nonexistent_movie(client, auth_headers):
    response = client.delete("/api/movies/99999", headers=auth_headers)
    assert response.status_code == 404
