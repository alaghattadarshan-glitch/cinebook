"""
Models package initializer.
Exports all models so SQLAlchemy discovers them during db.create_all().
"""

from app.models.base import db, BaseModel
from app.models.user import BaseUser, Customer, Admin
from app.models.movie import Movie
from app.models.theatre import Theatre, Screen, Seat
from app.models.show import Show, ShowSeat
from app.models.booking import Booking, BookingSeat, Payment, Ticket

__all__ = [
    "db",
    "BaseModel",
    "BaseUser",
    "Customer",
    "Admin",
    "Movie",
    "Theatre",
    "Screen",
    "Seat",
    "Show",
    "ShowSeat",
    "Booking",
    "BookingSeat",
    "Payment",
    "Ticket",
]
