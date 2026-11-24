"""
Database Seeder Service.
Initializes default Admin, sample Theatres, Screens, Seats, and Shows.
Ensures that the application is immediately testable and functional upon launch.
"""

from datetime import datetime, timedelta
from app.models.base import db
from app.models.user import Admin, Customer
from app.models.theatre import Theatre, Screen, Seat
from app.models.movie import Movie
from app.models.show import Show, ShowSeat
from app.core.interfaces import SeatTier
from app.services.tmdb_service import TMDBService


class SeedService:
    """Seeds initial administrative user, theatres, screens, and shows."""

    @staticmethod
    def seed_all():
        # 1. Seed Movies via TMDBService
        tmdb_service = TMDBService()
        tmdb_service.sync_catalog()

        # 2. Seed Default Admin and Demo Customer
        if not Admin.query.filter_by(email="admin@cinebook.com").first():
            admin = Admin(
                name="Cinebook Master Admin",
                email="admin@cinebook.com",
                password="adminpassword123",
                phone="+919876543210"
            )
            db.session.add(admin)

        if not Customer.query.filter_by(email="user@cinebook.com").first():
            customer = Customer(
                name="John Doe",
                email="user@cinebook.com",
                password="userpassword123",
                phone="+919123456780"
            )
            db.session.add(customer)

        # 3. Seed Theatres & Screens
        theatres_data = [
            {
                "name": "PVR ICON Cinemas",
                "city": "Mumbai",
                "location": "Phoenix Palladium, Lower Parel",
                "address": "462, Senapati Bapat Marg, Lower Parel, Mumbai",
                "screens": [
                    {"number": "Screen 1 - IMAX with Laser", "sound": "Dolby 12.1", "type": "IMAX 3D"},
                    {"number": "Screen 2 - Atmos Gold Class", "sound": "Dolby Atmos", "type": "Gold Class"}
                ]
            },
            {
                "name": "INOX Megaplex",
                "city": "Bengaluru",
                "location": "Mall of Asia, Bellary Road",
                "address": "Byatarayanapura, Bellary Rd, Bengaluru",
                "screens": [
                    {"number": "Screen 1 - Laser 4K", "sound": "Dolby Atmos 7.1", "type": "Laser 4K"},
                    {"number": "Screen 2 - Insignia", "sound": "Dolby Atmos", "type": "Luxury Recliner"}
                ]
            },
            {
                "name": "Cinepolis VIP",
                "city": "Delhi NCR",
                "location": "DLF Avenue, Saket",
                "address": "Press Enclave Marg, Saket, New Delhi",
                "screens": [
                    {"number": "Screen 1 - 4DX", "sound": "Dolby Atmos", "type": "4DX Experience"},
                    {"number": "Screen 2 - RealD 3D", "sound": "Dolby 7.1", "type": "Standard Digital"}
                ]
            }
        ]

        for t_data in theatres_data:
            theatre = Theatre.query.filter_by(name=t_data["name"]).first()
            if not theatre:
                theatre = Theatre(
                    name=t_data["name"],
                    city=t_data["city"],
                    location=t_data["location"],
                    address=t_data["address"]
                )
                db.session.add(theatre)
                db.session.flush()

                # Add screens and configure physical seating grid
                for s_data in t_data["screens"]:
                    screen = Screen(
                        theatre_id=theatre.id,
                        screen_number=s_data["number"],
                        sound_type=s_data["sound"],
                        screen_type=s_data["type"]
                    )
                    db.session.add(screen)
                    db.session.flush()

                    # Create standard cinema layout: Rows A-F (8 seats per row = 48 seats per screen)
                    # Rows A-B: RECLINER (Luxury)
                    # Rows C-D: PREMIUM
                    # Rows E-F: REGULAR
                    for row_char in ["A", "B", "C", "D", "E", "F"]:
                        tier = SeatTier.RECLINER.value if row_char in ("A", "B") else (
                            SeatTier.PREMIUM.value if row_char in ("C", "D") else SeatTier.REGULAR.value
                        )
                        for seat_num in range(1, 9):
                            seat = Seat(
                                screen_id=screen.id,
                                seat_row=row_char,
                                seat_number=seat_num,
                                tier=tier
                            )
                            db.session.add(seat)

        db.session.commit()

        # 4. Seed Shows for all active screens
        movies = Movie.query.all()
        screens = Screen.query.all()

        if movies and screens:
            now = datetime.utcnow()
            show_times_offsets = [
                (timedelta(hours=2), 220.0),
                (timedelta(hours=5), 250.0),
                (timedelta(hours=8), 300.0),
                (timedelta(days=1, hours=3), 250.0)
            ]

            for screen in screens:
                # Assign rotating movies
                for idx, (offset, base_price) in enumerate(show_times_offsets):
                    target_movie = movies[(screen.id + idx) % len(movies)]
                    start_t = now + offset
                    end_t = start_t + timedelta(minutes=target_movie.runtime + 20)

                    existing_show = Show.query.filter_by(
                        screen_id=screen.id,
                        start_time=start_t
                    ).first()

                    if not existing_show:
                        show = Show(
                            movie_id=target_movie.id,
                            screen_id=screen.id,
                            start_time=start_t,
                            end_time=end_t,
                            base_price=base_price
                        )
                        db.session.add(show)
                        db.session.flush()

                        # Populate ShowSeat inventory for this show with tiered pricing
                        for seat in screen.seats:
                            multiplier = 2.0 if seat.tier == SeatTier.RECLINER.value else (
                                1.4 if seat.tier == SeatTier.PREMIUM.value else 1.0
                            )
                            price = round(show.base_price * multiplier, 2)
                            show_seat = ShowSeat(
                                show_id=show.id,
                                seat_id=seat.id,
                                price=price,
                                status="AVAILABLE"
                            )
                            db.session.add(show_seat)

            db.session.commit()
