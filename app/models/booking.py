"""
Booking, BookingSeat, Payment, and Ticket Models.
Demonstrates:
- Composition: Booking owns BookingSeats, Payment and Ticket.
- Encapsulation: Validations, state transitions, total computation.
- Financial Consistency: Recording transaction history and ticket verification identifiers.
"""

import uuid
from datetime import datetime
from app.models.base import db, BaseModel
from app.core.interfaces import BookingStatus, PaymentMethod, PaymentStatus


class Booking(BaseModel):
    """
    Booking Aggregate Root.
    Demonstrates:
    - Encapsulation: Enforces status transitions (PENDING -> CONFIRMED / CANCELLED).
    - Composition: Deleting a booking deletes associated seats, payment and ticket records.
    """
    __tablename__ = "bookings"

    booking_reference = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    show_id = db.Column(db.Integer, db.ForeignKey("shows.id", ondelete="CASCADE"), nullable=False, index=True)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default=BookingStatus.PENDING.value, nullable=False, index=True)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = db.relationship("BaseUser", back_populates="bookings")
    show = db.relationship("Show", back_populates="bookings")
    booking_seats = db.relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan", lazy="selectin")
    payment = db.relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    ticket = db.relationship("Ticket", back_populates="booking", uselist=False, cascade="all, delete-orphan")

    @classmethod
    def generate_booking_ref(cls) -> str:
        """Class Method: Generates a human-friendly unique reference code (e.g., CNB-2025-A1B2C3)."""
        return f"CNB-{datetime.utcnow().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

    @property
    def seat_codes(self) -> str:
        """Encapsulation: Returns comma-separated seat numbers (e.g., 'A1, A2, A3')."""
        return ", ".join(bs.seat_code for bs in self.booking_seats)

    @property
    def can_cancel(self) -> bool:
        """
        Encapsulation: Business rule for booking cancellation.
        Can only cancel if confirmed and the show starts at least 2 hours in the future.
        """
        if self.status != BookingStatus.CONFIRMED.value:
            return False
        if not self.show or not self.show.start_time:
            return False
        return datetime.utcnow() + datetime.timedelta(hours=2) <= self.show.start_time

    def __repr__(self) -> str:
        return f"<Booking id={self.id} ref='{self.booking_reference}' status='{self.status}' amount={self.total_amount}>"


class BookingSeat(BaseModel):
    """
    Association Entity linking a Booking with the individual seats booked and their finalized price.
    """
    __tablename__ = "booking_seats"

    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    show_seat_id = db.Column(db.Integer, db.ForeignKey("show_seats.id", ondelete="CASCADE"), nullable=False, index=True)
    seat_code = db.Column(db.String(10), nullable=False)
    seat_tier = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Relationships
    booking = db.relationship("Booking", back_populates="booking_seats")
    show_seat = db.relationship("ShowSeat")

    def __repr__(self) -> str:
        return f"<BookingSeat booking_id={self.booking_id} seat='{self.seat_code}' price={self.price}>"


class Payment(BaseModel):
    """
    Payment Transaction Record.
    Demonstrates:
    - Encapsulation of financial audit trail.
    - Association with Booking.
    """
    __tablename__ = "payments"

    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    payment_method = db.Column(db.String(20), nullable=False)  # UPI, CARD, CASH
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default=PaymentStatus.SUCCESS.value, nullable=False)
    payment_details = db.Column(db.String(255), nullable=True)  # Masked card, UPI VPA, or counter id
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    booking = db.relationship("Booking", back_populates="payment")

    def __repr__(self) -> str:
        return f"<Payment id={self.id} txn='{self.transaction_id}' method='{self.payment_method}' amount={self.amount}>"


class Ticket(BaseModel):
    """
    Digital Ticket Entity.
    Demonstrates:
    - Encapsulation of digital verification QR code and secure token.
    - Composition with Booking.
    """
    __tablename__ = "tickets"

    ticket_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    qr_code_path = db.Column(db.String(255), nullable=True)
    qr_data = db.Column(db.Text, nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    booking = db.relationship("Booking", back_populates="ticket")

    @classmethod
    def generate_ticket_number(cls) -> str:
        """Class Method: Generates digital ticket barcode/ticket number."""
        return f"TKT-{uuid.uuid4().hex[:10].upper()}"

    def __repr__(self) -> str:
        return f"<Ticket id={self.id} number='{self.ticket_number}' is_used={self.is_used}>"
