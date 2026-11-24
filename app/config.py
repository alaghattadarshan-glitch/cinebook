import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseConfig:
    """Base Configuration Class (Encapsulating default application settings)."""

    # Secret key for session management and CSRF protection
    SECRET_KEY = os.getenv("SECRET_KEY", "cinebook-production-security-default-key")

    # Database configuration
    # Supports MySQL or SQLite as an effortless local development fallback
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///cinebook.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    } if not SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {}

    # TMDB API Credentials
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
    TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    TMDB_IMAGE_BASE_URL = os.getenv("TMDB_IMAGE_BASE_URL", "https://image.tmdb.org/t/p/w500")
    TMDB_BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/original"

    # Business Logic Configuration
    SEAT_LOCK_TIMEOUT_MINUTES = int(os.getenv("SEAT_LOCK_TIMEOUT_MINUTES", 10))
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Static Assets & Fallbacks
    POSTER_FALLBACK = "/static/images/poster-fallback.svg"
    BANNER_FALLBACK = "/static/images/banner-fallback.svg"


class DevConfig(BaseConfig):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class ProdConfig(BaseConfig):
    """Production environment configuration with hardened security."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class TestConfig(BaseConfig):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    # In-memory SQLite for rapid, isolated unit and integration testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SEAT_LOCK_TIMEOUT_MINUTES = 2


config_by_name = {
    "development": DevConfig,
    "production": ProdConfig,
    "testing": TestConfig,
    "default": DevConfig,
}
