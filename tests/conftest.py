"""
Pytest Test Configuration & Shared Fixtures.
"""

import pytest
from app import create_app
from app.models.base import db
from app.models.user import Customer, Admin
from app.models.movie import Movie
from app.models.theatre import Theatre, Screen, Seat
from app.models.show import Show, ShowSeat
from app.core.interfaces import SeatTier
from datetime import datetime, timedelta


@pytest.fixture(scope="session")
def app():
    """Create Flask application configured for isolated testing."""
    test_app = create_app("testing")
    with test_app.app_context():
        yield test_app


@pytest.fixture(scope="function")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Provides a clean database session for each test."""
    db.create_all()

    # Create basic test data
    admin = Admin(name="Test Admin", email="admin_test@cinebook.com", password="adminsecret123")
    customer = Customer(name="Test Customer", email="customer_test@cinebook.com", password="customersecret123", phone="+919876543210")
    db.session.add_all([admin, customer])

    # Movie
    movie = Movie(
        title="Interstellar",
        description="A team of explorers travel through a wormhole in space.",
        rating=8.7,
        runtime=169,
        language="English",
        category="NOW_SHOWING",
        poster_path="/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"
    )
    db.session.add(movie)
    db.session.flush()

    # Theatre & Screen
    theatre = Theatre(name="Cinebook Galaxy", city="Mumbai", location="Bandra West", address="Hill Road")
    db.session.add(theatre)
    db.session.flush()

    screen = Screen(theatre_id=theatre.id, screen_number="Screen 1 - Atmos", screen_type="IMAX", sound_type="Dolby Atmos")
    db.session.add(screen)
    db.session.flush()

    # Create 4 seats
    s1 = Seat(screen_id=screen.id, seat_row="A", seat_number=1, tier=SeatTier.REGULAR.value)
    s2 = Seat(screen_id=screen.id, seat_row="A", seat_number=2, tier=SeatTier.REGULAR.value)
    s3 = Seat(screen_id=screen.id, seat_row="B", seat_number=1, tier=SeatTier.PREMIUM.value)
    s4 = Seat(screen_id=screen.id, seat_row="C", seat_number=1, tier=SeatTier.RECLINER.value)
    db.session.add_all([s1, s2, s3, s4])
    db.session.flush()

    # Show
    show = Show(
        movie_id=movie.id,
        screen_id=screen.id,
        start_time=datetime.utcnow() + timedelta(days=1),
        end_time=datetime.utcnow() + timedelta(days=1, hours=3),
        base_price=200.0
    )
    db.session.add(show)
    db.session.flush()

    for seat in [s1, s2, s3, s4]:
        mult = 2.0 if seat.tier == "RECLINER" else (1.4 if seat.tier == "PREMIUM" else 1.0)
        ss = ShowSeat(show_id=show.id, seat_id=seat.id, price=show.base_price * mult, status="AVAILABLE")
        db.session.add(ss)

    db.session.commit()

    yield db.session

    db.session.rollback()
    db.drop_all()
