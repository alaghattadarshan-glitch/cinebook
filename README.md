# CINEBOOK - Industry-Standard Movie Ticket Booking System

**CINEBOOK** is an enterprise-grade, full-stack Movie Ticket Booking application inspired by BookMyShow. It is specifically engineered to demonstrate strong practical knowledge of **Object-Oriented Programming (OOP) in Python**, clean layered architecture, dynamic seat concurrency control, TMDB API synchronization, digital QR ticket generation, and containerization.

---

## 🌟 Key Features

- **Object-Oriented Design**: Pure implementation of Encapsulation, Inheritance, Polymorphism, Abstraction (ABC), Strategy Pattern, Factory Pattern, and SOLID principles.
- **Visual & Interactive Seating Layout**: Real-time cinema seat map categorizing Regular, Premium, and Recliner seats.
- **Seat Concurrency & Double-Booking Prevention**: High-integrity seat locking with automatic timeout expiration and atomic database transactions.
- **Real TMDB API Integration**: Dynamically pulls real movie titles, genres, overviews, ratings, and high-definition official posters from The Movie Database (TMDB) with graceful SVG fallbacks.
- **Polymorphic Payment Processing**: Simulated payment gateways (UPI with VPA validation, Credit/Debit Cards with Luhn checksum and masking, and Box Office Counter Cash).
- **Digital Tickets & QR Verification**: Auto-generates scannable QR codes containing encrypted booking verification payloads and provides instant downloadable PDF tickets.
- **Administrator Dashboard**: Full management portal for synchronizing TMDB movies, scheduling shows, managing screens, configuring ticket tier pricing, and tracking revenue.
- **Dark Cinematic UI/UX**: Responsive BookMyShow-inspired theme crafted with CSS custom properties, grid layouts, and smooth animations.

---

## 🏗️ System Architecture & Folder Structure

CINEBOOK follows a strictly decoupled, **Layered Architecture** adhering to the Single Responsibility Principle:

```
cinebook/
├── app/
│   ├── __init__.py           # Application Factory (create_app), extension initialization
│   ├── config.py             # Encapsulated Environment Configuration classes
│   ├── core/                 # Pure OOP Domain & Abstract Interfaces
│   │   ├── interfaces.py     # Abstract Base Classes (ABCs): PaymentProcessor, PricingStrategy
│   │   ├── payment.py        # Inheritance Hierarchy: BasePayment -> Upi, Card, Cash
│   │   ├── pricing.py        # Strategy Pattern: Standard, Weekend, ReclinerLuxury
│   │   └── notifications.py  # Abstraction: Email & SMS Notification services
│   ├── models/               # SQLAlchemy ORM Entities (Rich Domain Models)
│   │   ├── base.py           # BaseModel with timestamps & serialization
│   │   ├── user.py           # Inheritance: BaseUser -> Customer, Admin
│   │   ├── movie.py          # Movie entity with TMDB mappings & safe URL accessors
│   │   ├── theatre.py        # Composition: Theatre owns Screens; Screen owns Seats
│   │   ├── show.py           # Show and ShowSeat (Concurrency & runtime status tracking)
│   │   └── booking.py        # Booking aggregate, BookingSeat, Payment, and Ticket
│   ├── repositories/         # Repository Pattern: Isolated data-access logic
│   ├── services/             # Business Logic & Orchestration
│   │   ├── tmdb_service.py   # TMDB client with caching & offline seed catalog
│   │   ├── booking_service.py# Seat locking, validation & confirmation
│   │   ├── payment_service.py# Polymorphic payment executor
│   │   ├── ticket_service.py # QR Code & ReportLab PDF generator
│   │   └── seed_service.py   # Database seeder for demo venues & users
│   ├── routes/               # Flask Blueprints (Presentation Layer)
│   │   ├── main.py           # Home, City selector, Filtered Discovery
│   │   ├── auth.py           # Customer Registration, Login & Profile
│   │   ├── movies.py         # Movie details & showtimes by cinema
│   │   ├── booking.py        # Seat selection, lock API, Checkout & Payment
│   │   ├── tickets.py        # Digital ticket view & PDF download
│   │   └── admin.py          # Role-based Administrator control portal
│   ├── templates/            # Semantic Jinja2 Templates (Dark Theme)
│   └── static/               # Assets (CSS variables, Modular JS, SVGs)
├── tests/                    # Pytest test suite covering OOP, DB, and Web flows
├── docker/                   # MySQL init scripts
├── Dockerfile                # Multi-stage production container
├── docker-compose.yml        # Orchestrates Flask Web & MySQL 8.0 services
├── requirements.txt          # Python dependencies
├── run.py                    # Entry point script
└── README.md                 # Documentation
```

---

## 🧩 Deep Dive: Practical OOP Implementation

### 1. Encapsulation
- **Protected State**: Attributes such as `BaseUser._password_hash` and `BasePayment._amount` are protected.
- **Properties & Invariant Setters**: 
  - `User.password`: Disallows reading plain text and generates cryptographic bcrypt/pbkdf2 salted hashes.
  - `BasePayment.amount`: Validates that monetary values are strictly positive float numbers.
  - `Movie.poster_url`: Automatically provides a clean SVG placeholder if TMDB has no poster available.
  - `ShowSeat.is_available()`: Re-evaluates status dynamically based on whether temporary locks have expired.

### 2. Inheritance
- **User Hierarchy**:
  ```
  BaseUser (Flask-Login UserMixin)
      ├── Customer (Active bookings queries, past booking history)
      └── Admin (Elevated RBAC permissions, dashboard access)
  ```
- **Payment Hierarchy**:
  ```
  BasePayment (Abstract payment lifecycle, currency, transaction generator)
      ├── UpiPayment (VPA regex verification, instant authorization)
      ├── CardPayment (Masked credit card representation, Luhn verification)
      └── CashPayment (Box Office / Counter validation)
  ```

### 3. Polymorphism
- **Polymorphic Payment Processing**: `PaymentProcessor.process_payment()` is invoked uniformly across UPI, Card, and Cash without caller branch conditions.
- **Dynamic Pricing Strategies**:
  - `StandardPricingStrategy`: Flat multiplier based on physical tier (Regular, Premium, Recliner).
  - `WeekendPricingStrategy`: Dynamically introduces a +20% weekend surge factor for Friday, Saturday, and Sunday screenings.
  - `ReclinerLuxuryStrategy`: Luxury VIP surcharge with included gourmet concessions.

### 4. Abstraction
- Python's `abc.ABC` and `@abstractmethod` decorators define explicit interfaces in `app/core/interfaces.py`:
  - `PaymentProcessor`
  - `TicketPricingStrategy`
  - `NotificationService`

### 5. SOLID Principles & Additional Patterns
- **Single Responsibility (SRP)**: Routes only handle HTTP; Repositories handle queries; Services orchestrate business logic.
- **Open/Closed Principle (OCP)**: New payment types or pricing models can be added by implementing interfaces without modifying `BookingService`.
- **Liskov Substitution (LSP)**: All `BaseUser` and `BasePayment` subclasses can be substituted anywhere the base class is expected.
- **Factory Method Pattern**: `PaymentFactory.create_payment(...)` creates the appropriate subclass dynamically.
- **Composition & Aggregation**:
  - A `Theatre` **has** multiple `Screen`s (Composition - deleting theatre cascades to screens).
  - A `Screen` **has** multiple physical `Seat`s (Composition).
  - A `Show` **aggregates** a `Movie` and a `Screen`.

---

## 🗄️ Database Schema & Concurrency Design

CINEBOOK uses a normalized relational model (MySQL / SQLite compatible):

1. `users`: Customer and administrator accounts with polymorphic roles.
2. `movies`: Cached metadata (title, overview, TMDB ID, backdrop, poster, rating, runtime, trailer).
3. `theatres`: Venues grouped by city with address and location.
4. `screens`: Individual auditoriums (IMAX, 4DX, Dolby Atmos).
5. `seats`: Physical rows ('A', 'B', 'C') and numbers (1-8) with physical tiers (`REGULAR`, `PREMIUM`, `RECLINER`).
6. `shows`: Scheduled movie screenings tied to a screen, date, and start/end time.
7. `show_seats`: **Per-Show runtime seat availability**:
   - `status`: `AVAILABLE`, `LOCKED`, or `BOOKED`
   - `locked_until`: UTC timestamp when temporary checkout lock expires
   - `locked_by_user_id` & `locked_by_session_id`: Owner of temporary reservation
8. `bookings`: Master booking aggregate with unique reference (e.g. `CNB-202506-A1B2C3`).
9. `booking_seats`: Exact seats linked to a confirmed booking.
10. `payments`: Audit ledger storing transaction ID, payment method, amount, and timestamp.
11. `tickets`: Digital gate pass with encrypted QR payload and ticket barcode.

### Preventing Double Booking
When a user selects seats and proceeds to checkout:
1. `BookingService.lock_seats_for_checkout()` validates that no chosen seat is `BOOKED` or actively `LOCKED` by another user.
2. It sets `status = LOCKED` and stamps `locked_until = now() + 10 minutes`.
3. If payment succeeds, seats transition atomically to `BOOKED`. If the checkout is abandoned, the lock automatically expires and is released for other customers.

---

## 🚀 Quickstart & Installation

### Option 1: Local Development (Virtual Environment)

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd "movie ticket"
   ```

2. **Create and activate Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   ```
   *(Optional)* Add your free TMDB API Key from https://www.themoviedb.org/settings/api into `TMDB_API_KEY` in `.env`. If left empty, CINEBOOK automatically loads an offline catalog with real TMDB movie data and poster paths!

5. **Run the Application**:
   ```bash
   python run.py
   ```
   Open your browser at **http://127.0.0.1:5000**

---

### Option 2: Docker & Docker Compose (Production Ready)

Start the entire stack (Flask app + MySQL 8.0 container):

```bash
docker compose up --build
```

Access the application at **http://localhost:5000**.

---

## 🔑 Default Demo Accounts

Upon initial launch, the database automatically seeds with venues, movies, showtimes, and two accounts:

| Role | Email | Password |
|---|---|---|
| **Administrator** | `admin@cinebook.com` | `adminpassword123` |
| **Customer** | `user@cinebook.com` | `userpassword123` |

---

## 🧪 Running the Test Suite

The comprehensive test suite verifies OOP architecture, seat locking, payment polymorphism, and API fallbacks:

```bash
source venv/bin/activate
PYTHONPATH=. pytest -v
```

To run with coverage reporting:
```bash
PYTHONPATH=. pytest --cov=app tests/
```

---

## 📄 License
This project is developed as an academic and professional demonstration of Object-Oriented Software Engineering and Python Flask architecture.
