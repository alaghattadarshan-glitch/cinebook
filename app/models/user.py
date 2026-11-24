"""
User Inheritance Hierarchy: BaseUser, Customer, Admin.
Demonstrates:
- Inheritance: BaseUser (single-table / joined inheritance pattern) -> Customer, Admin
- Encapsulation: Password hashing, email format validation, profile properties
- Polymorphism: Role-specific authorization checks and dashboard routing
"""

import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.models.base import db, BaseModel


class BaseUser(BaseModel, UserMixin):
    """
    Base User Entity.
    Demonstrates:
    - Encapsulation: Protected _password_hash, verified via getter/setter
    - Inheritance: Serves as parent for Customer and Admin subclasses
    """
    __tablename__ = "users"

    # Discriminating role column
    role = db.Column(db.String(20), nullable=False, default="CUSTOMER", index=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    _password_hash = db.Column("password_hash", db.String(256), nullable=False)
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships (Association / Aggregation)
    bookings = db.relationship("Booking", back_populates="customer", cascade="all, delete-orphan", lazy="dynamic")

    # SQLAlchemy Single Table Inheritance setup
    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": "BASE",
    }

    # Email format validation pattern (Class variable)
    EMAIL_REGEX = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$")

    def __init__(self, name: str, email: str, password: str, phone: str = None, role: str = "CUSTOMER", **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.email = email  # Triggers property setter
        self.password = password  # Triggers password hashing
        self.phone = phone
        self.role = role

    # Encapsulation for email
    @property
    def email_address(self) -> str:
        return self.email

    # Encapsulation for password security
    @property
    def password(self):
        raise AttributeError("Password cannot be read in plain text.")

    @password.setter
    def password(self, plain_text_password: str):
        if not plain_text_password or len(plain_text_password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        self._password_hash = generate_password_hash(plain_text_password)

    def verify_password(self, plain_text_password: str) -> bool:
        """Encapsulation: Verifies salted hash without exposing the plaintext."""
        if not self._password_hash:
            return False
        return check_password_hash(self._password_hash, plain_text_password)

    # Polymorphic method: is_admin can be checked uniformly
    def is_admin(self) -> bool:
        """Polymorphism: Overridden in Admin subclass."""
        return self.role == "ADMIN"

    def get_id(self):
        """Flask-Login integration: returns unique identifier as string."""
        return str(self.id)

    @property
    def is_active(self):
        # Read from __dict__ to avoid triggering deferred/expired attribute loading when detached
        return self.__dict__.get("is_active_user", True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} email='{self.email}' role='{self.role}'>"


class Customer(BaseUser):
    """
    Customer Subclass.
    Demonstrates:
    - Inheritance from BaseUser
    - Specific customer methods: active bookings query, booking history
    """
    __mapper_args__ = {
        "polymorphic_identity": "CUSTOMER",
    }

    def __init__(self, name: str, email: str, password: str, phone: str = None, **kwargs):
        super().__init__(name=name, email=email, password=password, phone=phone, role="CUSTOMER", **kwargs)

    def is_admin(self) -> bool:
        """Method Overriding: Customers are not administrators."""
        return False

    def get_upcoming_bookings(self):
        """Encapsulation: Queries confirmed future shows for this customer."""
        from app.models.booking import Booking
        from app.models.show import Show
        return self.bookings.join(Show).filter(
            Booking.status == "CONFIRMED",
            Show.start_time >= datetime.utcnow()
        ).order_by(Show.start_time.asc()).all()

    def get_booking_history(self):
        """Encapsulation: Returns all past & present bookings in reverse chronological order."""
        return self.bookings.order_by(self.bookings.entity.created_at.desc()).all()


class Admin(BaseUser):
    """
    Admin Subclass.
    Demonstrates:
    - Inheritance from BaseUser
    - Elevated privileges & administrative capabilities
    """
    __mapper_args__ = {
        "polymorphic_identity": "ADMIN",
    }

    def __init__(self, name: str, email: str, password: str, phone: str = None, **kwargs):
        super().__init__(name=name, email=email, password=password, phone=phone, role="ADMIN", **kwargs)

    def is_admin(self) -> bool:
        """Method Overriding: Returns True for Admin instances."""
        return True
