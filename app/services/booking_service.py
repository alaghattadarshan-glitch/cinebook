"""
Booking & Concurrency Service.
Demonstrates:
- Concurrency Control: Locking seats with expiration timeouts
- Double Booking Prevention via Database Transactions & Row Locking
- Revalidation before payment confirmation
- Pricing calculation using Strategy Pattern
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import or_

from app.models.base import db
from app.models.show import Show, ShowSeat
from app.models.theatre import Seat
from app.models.booking import Booking, BookingSeat
from app.core.interfaces import SeatStatus, BookingStatus, SeatTier
from app.core.pricing import PricingContext, StandardPricingStrategy, WeekendPricingStrategy


class BookingService:
    """
    Booking Domain Service.
    Coordinates seat locking, pricing computation, checkout, and cancellation workflows.
    """

    def __init__(self, lock_timeout_minutes: int = 10):
        self._lock_timeout_minutes = lock_timeout_minutes
        self._pricing_context = PricingContext(StandardPricingStrategy())

    def get_show_seating_layout(self, show_id: int, current_user_id: int = None, session_id: str = None) -> Dict[str, Any]:
        """
        Retrieves complete seat matrix for a show categorized by Row and Tier.
        Automatically cleans up expired locks during traversal.
        """
        show = Show.query.get(show_id)
        if not show:
            raise ValueError(f"Show with id {show_id} does not exist.")

        # Clean expired locks for this show
        self.release_expired_locks(show_id=show_id)

        show_seats = ShowSeat.query.filter_by(show_id=show_id).join(Seat).order_by(Seat.seat_row.asc(), Seat.seat_number.asc()).all()

        rows_dict: Dict[str, List[Dict[str, Any]]] = {}
        for ss in show_seats:
            row_key = ss.seat.seat_row
            if row_key not in rows_dict:
                rows_dict[row_key] = []

            # Determine client-facing status
            resolved_status = ss.status
            if ss.status == SeatStatus.LOCKED.value:
                if (current_user_id and ss.locked_by_user_id == current_user_id) or (session_id and ss.locked_by_session_id == session_id):
                    resolved_status = "SELECTED_BY_YOU"
                else:
                    resolved_status = "LOCKED"

            rows_dict[row_key].append({
                "show_seat_id": ss.id,
                "seat_id": ss.seat.id,
                "seat_code": ss.seat.seat_code,
                "row": ss.seat.seat_row,
                "number": ss.seat.seat_number,
                "tier": ss.seat.tier,
                "price": ss.price,
                "status": resolved_status,
                "is_available": ss.is_available(current_user_id=current_user_id, session_id=session_id)
            })

        return {
            "show_id": show.id,
            "movie_title": show.movie.title,
            "theatre_name": show.theatre.name,
            "screen_name": show.screen.screen_number,
            "show_time": show.formatted_time,
            "show_date": show.formatted_date,
            "base_price": show.base_price,
            "layout": rows_dict
        }

    def release_expired_locks(self, show_id: int = None) -> int:
        """
        Finds and releases any seats whose temporary lock period has expired.
        """
        query = ShowSeat.query.filter(
            ShowSeat.status == SeatStatus.LOCKED.value,
            ShowSeat.locked_until <= datetime.utcnow()
        )
        if show_id:
            query = query.filter(ShowSeat.show_id == show_id)

        expired_seats = query.all()
        released = 0
        for seat in expired_seats:
            seat.release_lock()
            released += 1

        if released > 0:
            db.session.commit()
        return released

    def lock_seats_for_checkout(self, show_id: int, show_seat_ids: List[int], user_id: int, session_id: str) -> Tuple[bool, str, float]:
        """
        Atomically locks selected seats for checkout.
        Demonstrates:
        - Concurrency protection
        - Revalidates that none of the chosen seats are booked or actively locked by another user.
        - Calculates total price dynamically.
        """
        if not show_seat_ids:
            return False, "No seats selected.", 0.0

        # Purge stale locks first
        self.release_expired_locks(show_id=show_id)

        # Use database transaction
        try:
            # Query seats with pessimistic lock semantics if supported, or select by IDs
            seats_to_lock = ShowSeat.query.filter(
                ShowSeat.show_id == show_id,
                ShowSeat.id.in_(show_seat_ids)
            ).all()

            if len(seats_to_lock) != len(show_seat_ids):
                return False, "One or more requested seats could not be found.", 0.0

            total_amount = 0.0
            for ss in seats_to_lock:
                if not ss.is_available(current_user_id=user_id, session_id=session_id):
                    return False, f"Seat {ss.seat.seat_code} is already booked or being booked by another customer.", 0.0

                success = ss.acquire_lock(
                    user_id=user_id,
                    session_id=session_id,
                    timeout_minutes=self._lock_timeout_minutes
                )
                if not success:
                    db.session.rollback()
                    return False, f"Failed to acquire lock for seat {ss.seat.seat_code}.", 0.0

                total_amount += ss.price

            db.session.commit()
            return True, "Seats successfully locked.", round(total_amount, 2)

        except Exception as e:
            db.session.rollback()
            return False, f"Database transaction error: {str(e)}", 0.0

    def confirm_booking(self, show_id: int, show_seat_ids: List[int], user_id: int, session_id: str) -> Optional[Booking]:
        """
        Finalizes booking after payment succeeds:
        - Revalidates seat locks
        - Converts ShowSeat state to BOOKED
        - Creates Booking and BookingSeat association entities
        """
        # Revalidate availability and ownership of lock
        seats = ShowSeat.query.filter(
            ShowSeat.show_id == show_id,
            ShowSeat.id.in_(show_seat_ids)
        ).all()

        if len(seats) != len(show_seat_ids):
            raise ValueError("Seat verification failed during confirmation.")

        for ss in seats:
            if ss.status == SeatStatus.BOOKED.value:
                raise ValueError(f"Seat {ss.seat.seat_code} was already booked.")
            if ss.status == SeatStatus.LOCKED.value:
                # Must be locked by this user or session
                if ss.locked_by_user_id != user_id and ss.locked_by_session_id != session_id:
                    raise ValueError(f"Lock for seat {ss.seat.seat_code} belongs to another user.")

        # Create Booking
        total_amount = sum(ss.price for ss in seats)
        booking = Booking(
            booking_reference=Booking.generate_booking_ref(),
            user_id=user_id,
            show_id=show_id,
            total_amount=round(total_amount, 2),
            status=BookingStatus.CONFIRMED.value,
            booking_time=datetime.utcnow()
        )
        db.session.add(booking)
        db.session.flush()  # Populates booking.id

        # Attach BookingSeats and mark ShowSeats as permanently booked
        for ss in seats:
            b_seat = BookingSeat(
                booking_id=booking.id,
                show_seat_id=ss.id,
                seat_code=ss.seat.seat_code,
                seat_tier=ss.seat.tier,
                price=ss.price
            )
            db.session.add(b_seat)
            ss.confirm_booking()

        db.session.commit()
        return booking

    def cancel_booking(self, booking_id: int, user_id: int = None) -> Tuple[bool, str]:
        """
        Cancels an eligible booking:
        - Restores ShowSeat records back to AVAILABLE
        - Updates booking status to CANCELLED
        """
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, "Booking not found."

        if user_id and booking.user_id != user_id:
            return False, "Unauthorized cancellation attempt."

        if not booking.can_cancel:
            return False, "This booking cannot be cancelled (shows starting within 2 hours or non-confirmed bookings are non-refundable)."

        # Release booked seats back to AVAILABLE
        for b_seat in booking.booking_seats:
            if b_seat.show_seat:
                b_seat.show_seat.status = SeatStatus.AVAILABLE.value

        booking.status = BookingStatus.CANCELLED.value
        db.session.commit()
        return True, "Booking successfully cancelled and seats released."
