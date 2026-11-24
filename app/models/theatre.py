"""
Theatre, Screen, and Physical Seat Models.
Demonstrates:
- Composition: A Theatre HAS screens; deleting a theatre cascades and destroys its screens.
- Composition: A Screen HAS physical seats; deleting a screen cascades and destroys its seats.
- Encapsulation: Calculating total capacities and tier distributions.
"""

from app.models.base import db, BaseModel
from app.core.interfaces import SeatTier


class Theatre(BaseModel):
    """
    Theatre / Multiplex Entity.
    Demonstrates:
    - Composition: Aggregates multiple Screens.
    """
    __tablename__ = "theatres"

    name = db.Column(db.String(150), nullable=False, index=True)
    city = db.Column(db.String(80), nullable=False, index=True)
    location = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Composition: A theatre owns its screens
    screens = db.relationship("Screen", back_populates="theatre", cascade="all, delete-orphan", lazy="selectin")

    @property
    def total_screens(self) -> int:
        return len(self.screens)

    @property
    def total_capacity(self) -> int:
        """Encapsulation: Aggregates capacity across all active screens."""
        return sum(s.capacity for s in self.screens if s.is_active)

    def __repr__(self) -> str:
        return f"<Theatre id={self.id} name='{self.name}' city='{self.city}'>"


class Screen(BaseModel):
    """
    Cinema Screen / Audi Model.
    Demonstrates:
    - Composition with Theatre (child of Theatre)
    - Composition with Seat (parent of Seats)
    """
    __tablename__ = "screens"

    theatre_id = db.Column(db.Integer, db.ForeignKey("theatres.id", ondelete="CASCADE"), nullable=False, index=True)
    screen_number = db.Column(db.String(50), nullable=False)  # e.g., "Screen 1 - Dolby Atmos"
    sound_type = db.Column(db.String(50), default="Dolby Atmos 7.1")
    screen_type = db.Column(db.String(50), default="IMAX 2D")
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    theatre = db.relationship("Theatre", back_populates="screens")
    seats = db.relationship("Seat", back_populates="screen", cascade="all, delete-orphan", lazy="selectin")
    shows = db.relationship("Show", back_populates="screen", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def capacity(self) -> int:
        """Dynamic capacity calculated from physical configured seats."""
        return len(self.seats)

    def __repr__(self) -> str:
        return f"<Screen id={self.id} theatre_id={self.theatre_id} name='{self.screen_number}'>"


class Seat(BaseModel):
    """
    Physical Seat Model belonging to a Screen.
    Important:
    A seat's physical tier, row, and column belong to the Screen.
    Its per-show availability and booking status are tracked separately in `ShowSeat`.
    """
    __tablename__ = "seats"

    screen_id = db.Column(db.Integer, db.ForeignKey("screens.id", ondelete="CASCADE"), nullable=False, index=True)
    seat_row = db.Column(db.String(5), nullable=False)  # e.g., 'A', 'B', 'C'
    seat_number = db.Column(db.Integer, nullable=False)  # e.g., 1, 2, 3
    tier = db.Column(db.String(20), default=SeatTier.REGULAR.value, nullable=False)  # REGULAR, PREMIUM, RECLINER

    # Ensure unique seat coordinates within a screen
    __table_args__ = (
        db.UniqueConstraint("screen_id", "seat_row", "seat_number", name="uq_screen_seat_coord"),
    )

    # Relationships
    screen = db.relationship("Screen", back_populates="seats")

    @property
    def seat_code(self) -> str:
        """Encapsulation: Returns formatted seat identifier like 'A1' or 'H12'."""
        return f"{self.seat_row}{self.seat_number}"

    def __repr__(self) -> str:
        return f"<Seat id={self.id} screen={self.screen_id} code='{self.seat_code}' tier='{self.tier}'>"
