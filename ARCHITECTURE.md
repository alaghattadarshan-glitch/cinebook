# CINEBOOK ARCHITECTURE & OOP DESIGN SPECIFICATION

## 1. System Overview
CINEBOOK is an industry-standard, modular movie ticket booking platform built with Python Flask, SQLAlchemy, MySQL, and modern HTML5/CSS3/JavaScript frontend inspired by BookMyShow. The core design rigorously demonstrates Object-Oriented Programming (OOP) concepts: Encapsulation, Inheritance, Polymorphism, Abstraction, and SOLID design principles.

## 2. Technology Stack
- **Backend Framework**: Python Flask (Application Factory pattern, Blueprints)
- **Database & ORM**: MySQL 8.0 (with SQLite fallback for lightweight development/testing), SQLAlchemy 2.0 ORM
- **External API**: TMDB (The Movie Database) API v3 with caching and graceful fallbacks
- **Template Engine**: Jinja2 with modern CSS variables, CSS grid/flexbox, interactive vanilla JavaScript
- **QR Code & PDF**: `qrcode` + Pillow / WeasyPrint / ReportLab / HTML5 Canvas / printable PDF templates
- **Testing**: pytest, pytest-cov
- **Containerization**: Dockerfile, docker-compose.yml

## 3. Modular Directory Structure
```
cinebook/
    app/
        __init__.py           # Application factory (create_app)
        config.py             # Config classes (BaseConfig, DevConfig, ProdConfig, TestConfig)
        models/               # SQLAlchemy ORM models + Domain classes
            __init__.py
            base.py           # BaseModel with timestamps & helpers
            user.py           # BaseUser, Customer, Admin
            movie.py          # Movie model with TMDB mapping
            theatre.py        # Theatre, Screen
            seat.py           # Seat, ShowSeat
            show.py           # Show model
            booking.py        # Booking, BookingSeat
            payment.py        # Payment entity
            ticket.py         # Ticket entity
        core/                 # Pure OOP Domain classes, Abstractions & Strategies
            __init__.py
            interfaces.py     # Abstract Base Classes (ABCs)
            pricing.py        # TicketPricingStrategy (Regular, Weekend, Holiday, Premium)
            payment.py        # BasePayment, UpiPayment, CardPayment, CashPayment (Polymorphism)
            notifications.py  # NotificationService ABC, EmailNotification, SMSNotification
        repositories/         # Data Access Layer (Repository Pattern)
            __init__.py
            base_repository.py
            user_repository.py
            movie_repository.py
            theatre_repository.py
            show_repository.py
            booking_repository.py
        services/             # Business Logic Layer
            __init__.py
            auth_service.py
            tmdb_service.py
            movie_service.py
            theatre_service.py
            booking_service.py
            payment_service.py
            ticket_service.py
        routes/               # Flask Blueprints (Presentation / Web layer)
            __init__.py
            main.py           # Home, Discovery, City selector
            auth.py           # Register, Login, Logout, Profile
            movies.py         # Movie details, listings
            booking.py        # Showtimes, Seat selection, Checkout, Payment
            tickets.py        # Ticket view, QR verification, Download PDF
            admin.py          # Admin dashboard, Theatre/Screen/Show/Movie management
        templates/
            base.html
            main/
                index.html
                discovery.html
            auth/
                login.html
                register.html
                profile.html
            movies/
                detail.html
            booking/
                showtimes.html
                seats.html
                checkout.html
                success.html
            tickets/
                view.html
            admin/
                dashboard.html
                movies.html
                theatres.html
                screens.html
                shows.html
                bookings.html
        static/
            css/
                style.css
                seats.css
                ticket.css
                admin.css
            js/
                main.js
                seats.js
                checkout.js
                admin.js
            images/
                logo.svg
                poster-fallback.svg
                banner-default.jpg
    tests/
        __init__.py
        conftest.py
        test_oop.py
        test_auth.py
        test_booking.py
        test_payments.py
        test_tmdb.py
        test_admin.py
    docker/
        init.sql
    .env.example
    requirements.txt
    Dockerfile
    docker-compose.yml
    run.py
    README.md
```

## 4. OOP Design & Principles Mapping
1. **Encapsulation**:
   - Private/protected attributes with `@property` and `@setter` with validation (e.g., `User.email`, `Seat.seat_number`, `Booking.total_amount`).
   - Strong invariant enforcement (cannot book already booked/locked seats, cannot pay negative amounts).
2. **Inheritance**:
   - `BaseUser` -> `Customer`, `Admin`
   - `BasePayment` -> `UpiPayment`, `CardPayment`, `CashPayment`
   - `TicketPricingStrategy` -> `StandardPricingStrategy`, `WeekendPricingStrategy`, `ReclinerLuxuryStrategy`
3. **Polymorphism**:
   - `PaymentProcessor.process_payment()` called polymorphically across UPI, Card, Cash.
   - `PricingStrategy.calculate_price(base_price, seat_tier, show_time)` called polymorphically.
4. **Abstraction**:
   - Python `abc.ABC` and `@abstractmethod` in `app/core/interfaces.py`.
   - Clear contract definitions for `PaymentProcessor`, `PricingStrategy`, `NotificationService`.
5. **Composition & Aggregation**:
   - `Theatre` has multiple `Screen`s (Composition).
   - `Screen` has multiple `Seat`s (Composition).
   - `Booking` has multiple `BookingSeat`s and one `Payment` (Composition/Association).
   - `Show` references `Movie` and `Screen` (Aggregation).
6. **Class Methods, Static Methods & Class Variables**:
   - Factory class methods (e.g. `Booking.create_pending_booking(...)`, `Seat.from_code(...)`).
   - Static utility methods for validation, QR payload hashing, formatting.
   - Class variables for seat tier price multipliers, seat lock timeouts.
