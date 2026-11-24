"""
OOP Abstraction: Notification Services.
Demonstrates:
- Abstraction: NotificationService interface
- Polymorphism: Email and SMS implementations
"""

import logging
from typing import Dict, Any
from app.core.interfaces import NotificationService

logger = logging.getLogger(__name__)


class EmailNotificationService(NotificationService):
    """Concrete Email notification sender (simulated for academic development)."""

    def send_booking_confirmation(self, customer_email: str, booking_details: Dict[str, Any]) -> bool:
        booking_id = booking_details.get("booking_id")
        movie_title = booking_details.get("movie_title")
        seats = booking_details.get("seats")
        logger.info(f"[EMAIL TO {customer_email}] Booking {booking_id} Confirmed! Movie: {movie_title}, Seats: {seats}")
        return True

    def send_cancellation_alert(self, customer_email: str, booking_details: Dict[str, Any]) -> bool:
        booking_id = booking_details.get("booking_id")
        logger.info(f"[EMAIL TO {customer_email}] Booking {booking_id} has been cancelled.")
        return True


class SMSNotificationService(NotificationService):
    """Concrete SMS notification sender."""

    def send_booking_confirmation(self, customer_phone: str, booking_details: Dict[str, Any]) -> bool:
        booking_id = booking_details.get("booking_id")
        logger.info(f"[SMS TO {customer_phone}] CINEBOOK: Booking {booking_id} confirmed. Enjoy your movie!")
        return True

    def send_cancellation_alert(self, customer_phone: str, booking_details: Dict[str, Any]) -> bool:
        booking_id = booking_details.get("booking_id")
        logger.info(f"[SMS TO {customer_phone}] CINEBOOK: Booking {booking_id} cancelled.")
        return True
