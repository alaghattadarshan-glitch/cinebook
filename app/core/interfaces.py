"""
OOP Abstractions and Interfaces for CINEBOOK.
Demonstrates:
- Abstraction: Python abc.ABC and @abstractmethod
- Interface Segregation Principle (ISP)
- Open/Closed Principle (OCP)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SeatTier(Enum):
    """Enumeration of physical seat tiers with corresponding display names."""
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    RECLINER = "RECLINER"


class SeatStatus(Enum):
    """Enumeration of show-specific seat availability states."""
    AVAILABLE = "AVAILABLE"
    SELECTED = "SELECTED"
    LOCKED = "LOCKED"
    BOOKED = "BOOKED"


class BookingStatus(Enum):
    """Enumeration of lifecycle statuses for a booking."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class PaymentMethod(Enum):
    """Enumeration of supported payment options."""
    UPI = "UPI"
    CARD = "CARD"
    CASH = "CASH"


class PaymentStatus(Enum):
    """Enumeration of payment execution statuses."""
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


@dataclass
class PaymentResult:
    """Value Object encapsulating the result of a payment operation."""
    success: bool
    transaction_id: str
    message: str
    payment_method: PaymentMethod
    amount: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


# =====================================================================
# 1. ABSTRACTION: PaymentProcessor Interface
# =====================================================================
class PaymentProcessor(ABC):
    """
    Abstract Base Class defining the contract for processing payments.
    Demonstrates:
    - Abstraction: Abstract methods enforce concrete implementations.
    - Polymorphism: Callers invoke `process_payment` uniformly regardless of whether
      the underlying strategy is UPI, Card, or Cash.
    """

    @abstractmethod
    def process_payment(self, amount: float, payment_data: Dict[str, Any]) -> PaymentResult:
        """
        Process a payment transaction.
        :param amount: Monetary sum to charge (must be > 0)
        :param payment_data: Dictionary containing method-specific payload (e.g. upi_id, card details)
        :return: PaymentResult instance
        """
        pass

    @abstractmethod
    def validate_payment_details(self, payment_data: Dict[str, Any]) -> bool:
        """Validate input payload for the specific payment gateway before executing payment."""
        pass


# =====================================================================
# 2. ABSTRACTION: TicketPricingStrategy Interface
# =====================================================================
class TicketPricingStrategy(ABC):
    """
    Abstract Strategy pattern for dynamic ticket pricing.
    Demonstrates:
    - Open/Closed Principle: New pricing models (e.g., Surge, Student, Holiday)
      can be added without altering existing booking code.
    - Polymorphism: Different pricing strategies compute prices via the identical method signature.
    """

    @abstractmethod
    def calculate_price(self, base_price: float, seat_tier: SeatTier, show_datetime: datetime) -> float:
        """
        Calculates the finalized single-ticket price based on tier, date/time, and strategy rules.
        :param base_price: Base price configured for the show
        :param seat_tier: SeatTier enum (REGULAR, PREMIUM, RECLINER)
        :param show_datetime: Date and time of the movie show
        :return: Computed ticket price
        """
        pass


# =====================================================================
# 3. ABSTRACTION: NotificationService Interface
# =====================================================================
class NotificationService(ABC):
    """
    Abstract interface for notifying customers regarding booking confirmations, cancellations, etc.
    """

    @abstractmethod
    def send_booking_confirmation(self, customer_email: str, booking_details: Dict[str, Any]) -> bool:
        """Dispatch a booking confirmation message/ticket to the customer."""
        pass

    @abstractmethod
    def send_cancellation_alert(self, customer_email: str, booking_details: Dict[str, Any]) -> bool:
        """Dispatch a booking cancellation notice to the customer."""
        pass
