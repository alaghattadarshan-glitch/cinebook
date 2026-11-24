"""
Integration Tests for Seat Locking, Double Booking Prevention & Concurrency.
"""

from app.models.show import Show, ShowSeat
from app.services.booking_service import BookingService
from app.services.payment_service import PaymentService
from app.models.user import Customer


def test_seat_selection_and_locking(db_session):
    """Test locking available seats for checkout."""
    show = Show.query.first()
    customer = Customer.query.filter_by(email="customer_test@cinebook.com").first()
    show_seats = ShowSeat.query.filter_by(show_id=show.id).limit(2).all()
    seat_ids = [ss.id for ss in show_seats]

    service = BookingService(lock_timeout_minutes=5)
    success, msg, total = service.lock_seats_for_checkout(
        show_id=show.id,
        show_seat_ids=seat_ids,
        user_id=customer.id,
        session_id="session_user_1"
    )

    assert success is True
    assert total > 0

    # Inspect seat status in database
    for sid in seat_ids:
        ss = ShowSeat.query.get(sid)
        assert ss.status == "LOCKED"
        assert ss.locked_by_user_id == customer.id


def test_double_booking_prevention(db_session):
    """Verify that a second customer cannot lock seats already locked by the first."""
    show = Show.query.first()
    c1 = Customer.query.filter_by(email="customer_test@cinebook.com").first()
    target_seat = ShowSeat.query.filter_by(show_id=show.id).first()

    service = BookingService(lock_timeout_minutes=10)

    # Customer 1 locks the seat
    ok1, _, _ = service.lock_seats_for_checkout(
        show_id=show.id,
        show_seat_ids=[target_seat.id],
        user_id=c1.id,
        session_id="session_c1"
    )
    assert ok1 is True

    # Customer 2 attempts to lock the exact same seat
    ok2, err_msg, _ = service.lock_seats_for_checkout(
        show_id=show.id,
        show_seat_ids=[target_seat.id],
        user_id=999,
        session_id="session_c2"
    )
    assert ok2 is False
    assert "already booked or being booked" in err_msg


def test_full_booking_and_payment_flow(db_session):
    """Complete End-to-End booking workflow test."""
    show = Show.query.first()
    customer = Customer.query.filter_by(email="customer_test@cinebook.com").first()
    seat = ShowSeat.query.filter_by(show_id=show.id).first()

    service = BookingService(lock_timeout_minutes=10)

    # 1. Lock seat
    ok, _, _ = service.lock_seats_for_checkout(
        show_id=show.id,
        show_seat_ids=[seat.id],
        user_id=customer.id,
        session_id="sess_full_flow"
    )
    assert ok is True

    # 2. Confirm booking
    booking = service.confirm_booking(
        show_id=show.id,
        show_seat_ids=[seat.id],
        user_id=customer.id,
        session_id="sess_full_flow"
    )
    assert booking is not None
    assert booking.status == "CONFIRMED"
    assert booking.booking_reference.startswith("CNB-")

    # 3. Process Payment
    pay_ok, pay_msg, payment = PaymentService.process_booking_payment(
        booking_id=booking.id,
        method="UPI",
        payment_payload={"upi_id": "testuser@okaxis"}
    )
    assert pay_ok is True
    assert payment.status == "SUCCESS"
    assert payment.payment_method == "UPI"
