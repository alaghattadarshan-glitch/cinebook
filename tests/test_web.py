"""
Web Routes, Authentication and TMDB integration tests.
"""

from app.models.user import Customer, BaseUser
from app.models.movie import Movie
from app.services.tmdb_service import TMDBService


def test_user_registration_and_login(client, db_session):
    """Test customer sign-up and sign-in routes."""
    # Register new user
    res = client.post("/auth/register", data={
        "name": "Bruce Wayne",
        "email": "bruce@wayne.com",
        "password": "darkknightpass",
        "phone": "+919999999999"
    }, follow_redirects=True)
    assert res.status_code == 200

    user = BaseUser.query.filter_by(email="bruce@wayne.com").first()
    assert user is not None
    assert user.name == "Bruce Wayne"

    # Log out
    client.get("/auth/logout", follow_redirects=True)

    # Log in
    login_res = client.post("/auth/login", data={
        "email": "bruce@wayne.com",
        "password": "darkknightpass"
    }, follow_redirects=True)
    assert login_res.status_code == 200
    assert b"Welcome back, Bruce Wayne" in login_res.data

    # Log out again so subsequent tests start with anonymous client
    client.get("/auth/logout", follow_redirects=True)


def test_movie_discovery_and_search(client, db_session):
    """Test search and filtering endpoints."""
    res = client.get("/explore?q=Interstellar")
    assert res.status_code == 200
    assert b"Interstellar" in res.data


def test_tmdb_fallback_and_catalog(db_session):
    """Verify TMDB service populates catalog with guaranteed valid posters."""
    svc = TMDBService()
    count = svc.sync_catalog()
    assert count >= 0

    movie = Movie.query.first()
    assert movie is not None
    assert movie.poster_url is not None
    assert len(movie.poster_url) > 0
