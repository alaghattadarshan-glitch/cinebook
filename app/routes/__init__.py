"""
Routes package initializer.
"""

from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.movies import movies_bp
from app.routes.booking import booking_bp
from app.routes.tickets import tickets_bp
from app.routes.admin import admin_bp

__all__ = [
    "main_bp",
    "auth_bp",
    "movies_bp",
    "booking_bp",
    "tickets_bp",
    "admin_bp"
]
