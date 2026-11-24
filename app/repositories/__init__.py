"""
Generic Base Repository and Specific Data Access Repositories.
Demonstrates:
- Repository Pattern (Decoupling Business Logic from Persistence)
- Generics and Code Reusability
- Encapsulation of Database Queries
"""

from typing import Type, TypeVar, Generic, List, Optional
from app.models.base import db, BaseModel
from app.models.user import BaseUser, Customer, Admin
from app.models.movie import Movie
from app.models.theatre import Theatre, Screen, Seat
from app.models.show import Show, ShowSeat
from app.models.booking import Booking, Payment, Ticket

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Generic CRUD Repository base class."""

    def __init__(self, model_class: Type[T]):
        self._model_class = model_class

    def get_by_id(self, entity_id: int) -> Optional[T]:
        return db.session.get(self._model_class, entity_id)

    def get_all(self) -> List[T]:
        return self._model_class.query.all()

    def add(self, entity: T) -> T:
        db.session.add(entity)
        db.session.commit()
        return entity

    def update(self, entity: T) -> T:
        db.session.commit()
        return entity

    def delete(self, entity: T) -> bool:
        db.session.delete(entity)
        db.session.commit()
        return True


class UserRepository(BaseRepository[BaseUser]):
    """User-specific Data Access Layer."""

    def __init__(self):
        super().__init__(BaseUser)

    def find_by_email(self, email: str) -> Optional[BaseUser]:
        if not email:
            return None
        return BaseUser.query.filter_by(email=email.strip().lower()).first()

    def get_all_customers(self) -> List[Customer]:
        return Customer.query.filter_by(role="CUSTOMER").all()


class MovieRepository(BaseRepository[Movie]):
    """Movie-specific Data Access Layer."""

    def __init__(self):
        super().__init__(Movie)

    def find_by_tmdb_id(self, tmdb_id: int) -> Optional[Movie]:
        return Movie.query.filter_by(tmdb_id=tmdb_id).first()

    def find_by_category(self, category: str) -> List[Movie]:
        return Movie.query.filter_by(category=category, is_active=True).all()

    def search_movies(self, query: str = None, language: str = None, genre: str = None, min_rating: float = None) -> List[Movie]:
        filters = [Movie.is_active.is_(True)]
        if query:
            filters.append(Movie.title.ilike(f"%{query.strip()}%"))
        if language and language.lower() != "all":
            filters.append(Movie.language.ilike(f"%{language.strip()}%"))
        if genre and genre.lower() != "all":
            filters.append(Movie.genre.ilike(f"%{genre.strip()}%"))
        if min_rating is not None and min_rating > 0:
            filters.append(Movie.rating >= min_rating)
        return Movie.query.filter(*filters).order_by(Movie.rating.desc()).all()


class TheatreRepository(BaseRepository[Theatre]):
    """Theatre Data Access Layer."""

    def __init__(self):
        super().__init__(Theatre)

    def get_all_active(self) -> List[Theatre]:
        return Theatre.query.filter_by(is_active=True).all()

    def get_distinct_cities(self) -> List[str]:
        rows = db.session.query(Theatre.city).filter_by(is_active=True).distinct().all()
        return sorted([r[0] for r in rows if r[0]])

    def get_theatres_by_city(self, city: str) -> List[Theatre]:
        return Theatre.query.filter_by(city=city, is_active=True).all()


class ShowRepository(BaseRepository[Show]):
    """Show and ShowSeat Data Access Layer."""

    def __init__(self):
        super().__init__(Show)

    def get_shows_for_movie_and_theatre(self, movie_id: int, theatre_id: int) -> List[Show]:
        return Show.query.join(Screen).filter(
            Show.movie_id == movie_id,
            Screen.theatre_id == theatre_id,
            Show.is_active.is_(True)
        ).order_by(Show.start_time.asc()).all()

    def get_show_seats(self, show_id: int) -> List[ShowSeat]:
        return ShowSeat.query.filter_by(show_id=show_id).join(Seat).order_by(Seat.seat_row.asc(), Seat.seat_number.asc()).all()

    def get_show_seat(self, show_id: int, seat_id: int) -> Optional[ShowSeat]:
        return ShowSeat.query.filter_by(show_id=show_id, seat_id=seat_id).first()


class BookingRepository(BaseRepository[Booking]):
    """Booking Data Access Layer."""

    def __init__(self):
        super().__init__(Booking)

    def find_by_reference(self, reference: str) -> Optional[Booking]:
        return Booking.query.filter_by(booking_reference=reference.strip()).first()

    def get_by_user(self, user_id: int) -> List[Booking]:
        return Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
