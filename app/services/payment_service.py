"""
Payment Service.
Demonstrates:
- Strategy / Polymorphism integration: Uses BasePayment subclasses polymorphically.
- Audit trail recording into MySQL.
- Coordinates Payment processing with Booking status.
"""

from typing import Dict, Any, Tuple
from app.models.base import db
from app.models.booking import Booking, Payment
from app.core.payment import PaymentFactory
from app.core.interfaces import PaymentStatus, BookingStatus


class PaymentService:
    """Service layer orchestrating simulated payment transactions."""

    @staticmethod
    def process_booking_payment(booking_id: int, method: str, payment_payload: Dict[str, Any]) -> Tuple[bool, str, Payment]:
        """
        Processes simulated payment polymorphically and records the transaction.
        """
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found.", None

        # Instantiate polymorphic payment processor via Factory
        try:
            payment_processor = PaymentFactory.create_payment(
                method=method,
                amount=booking.total_amount,
                **payment_payload
            )
        except Exception as e:
            return False, str(e), None

        # Execute polymorphic payment logic
        result = payment_processor.process_payment(
            amount=booking.total_amount,
            payment_data=payment_payload
        )

        # Record payment transaction in database
        payment_record = Payment(
            booking_id=booking.id,
            transaction_id=result.transaction_id or f"FAILED-{booking.booking_reference}",
            payment_method=result.payment_method.value,
            amount=result.amount,
            status=PaymentStatus.SUCCESS.value if result.success else PaymentStatus.FAILED.value,
            payment_details=payment_payload.get("upi_id") or getattr(payment_processor, "masked_card", "Counter")
        )
        db.session.add(payment_record)

        if not result.success:
            booking.status = BookingStatus.FAILED.value
            db.session.commit()
            return False, result.message, payment_record

        # Mark booking confirmed upon successful payment
        booking.status = BookingStatus.CONFIRMED.value
        db.session.commit()
        return True, result.message, payment_record
