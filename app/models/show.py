"""
Show and ShowSeat Models (Runtime Seat Status & Concurrency Control).
Demonstrates:
- Association between Movie, Screen, and Time slots.
- Separate per-show seat status tracking (ShowSeat) to maintain normalization and consistency.
- Encapsulation: Checking lock expirations and dynamic status resolution.
"""

from datetime import datetime, timedelta
from app.models.base import db, BaseModel
from app.core.interfaces import SeatStatus, SeatTier


class Show(BaseModel):
    """
    Movie Show Model.
    Associates a Movie with a Screen at a specific start and end time.
    """
    __tablename__ = "shows"

    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    screen_id = db.Column(db.Integer, db.ForeignKey("screens.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    base_price = db.Column(db.Float, nullable=False, default=150.0)  # INR
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    movie = db.relationship("Movie", back_populates="shows")
    screen = db.relationship("Screen", back_populates="shows")
    show_seats = db.relationship("ShowSeat", back_populates="show", cascade="all, delete-orphan", lazy="selectin")
    bookings = db.relationship("Booking", back_populates="show", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def theatre(self):
        """Convenience navigation: traverses Screen -> Theatre."""
        return self.screen.theatre if self.screen else None

    @property
    def formatted_time(self) -> str:
        return self.start_time.strftime("%I:%M %p")

    @property
    def formatted_date(self) -> str:
        return self.start_time.strftime("%A, %d %b %Y")

    def __repr__(self) -> str:
        return f"<Show id={self.id} movie_id={self.movie_id} screen_id={self.screen_id} time='{self.start_time}'>"


class ShowSeat(BaseModel):
    """
    Per-Show Seat State Model.
    Tracks whether a specific physical seat is AVAILABLE, LOCKED, or BOOKED for a particular show.
    Demonstrates:
    - Concurrency Control: locked_until timestamp and locked_by_session_id for multi-user safety.
    - Encapsulation: is_available() verifies both status and automatic lock timeout expiration.
    """
    __tablename__ = "show_seats"

    show_id = db.Column(db.Integer, db.ForeignKey("shows.id", ondelete="CASCADE"), nullable=False, index=True)
    seat_id = db.Column(db.Integer, db.ForeignKey("seats.id", ondelete="CASCADE"), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default=SeatStatus.AVAILABLE.value, nullable=False, index=True)

    # Concurrency / Seat Locking fields
    locked_until = db.Column(db.DateTime, nullable=True)
    locked_by_user_id = db.Column(db.Integer, nullable=True)
    locked_by_session_id = db.Column(db.String(100), nullable=True)

    # Unique constraint: Each physical seat has exactly ONE record per show
    __table_args__ = (
        db.UniqueConstraint("show_id", "seat_id", name="uq_show_seat"),
    )

    # Relationships
    show = db.relationship("Show", back_populates="show_seats")
    seat = db.relationship("Seat", lazy="joined")

    def is_available(self, current_user_id: int = None, session_id: str = None) -> bool:
        """
        Encapsulation: Determines if this seat can be selected.
        If locked but the lock time has elapsed, the seat is treated as automatically released.
        If currently locked by this exact user/session, it is available to proceed to payment.
        """
        if self.status == SeatStatus.BOOKED.value:
            return False

        if self.status == SeatStatus.LOCKED.value:
            if self.locked_until and datetime.utcnow() > self.locked_until:
                # Lock has expired; considered available
                return True
            # Seat is actively locked: check if locked by current user/session
            if current_user_id and self.locked_by_user_id == current_user_id:
                return True
            if session_id and self.locked_by_session_id == session_id:
                return True
            return False

        return True

    def acquire_lock(self, user_id: int, session_id: str, timeout_minutes: int = 10) -> bool:
        """
        Encapsulation & Mutator: Atomically locks seat for a checkout session.
        """
        if not self.is_available(current_user_id=user_id, session_id=session_id):
            return False

        self.status = SeatStatus.LOCKED.value
        self.locked_by_user_id = user_id
        self.locked_by_session_id = session_id
        self.locked_until = datetime.utcnow() + timedelta(minutes=timeout_minutes)
        return True

    def release_lock(self) -> None:
        """Releases temporary lock back to AVAILABLE state."""
        if self.status == SeatStatus.LOCKED.value:
            self.status = SeatStatus.AVAILABLE.value
            self.locked_until = None
            self.locked_by_user_id = None
            self.locked_by_session_id = None

    def confirm_booking(self) -> None:
        """Transitions seat state to permanently BOOKED."""
        self.status = SeatStatus.BOOKED.value
        self.locked_until = None
        self.locked_by_user_id = None
        self.locked_by_session_id = None

    def __repr__(self) -> str:
        return f"<ShowSeat id={self.id} show={self.show_id} seat={self.seat_id} status='{self.status}'>"
