"""
Booking & Interactive Seating Routes.
Demonstrates:
- Visual Seating Layout
- Temporary seat locking during checkout
- Double booking prevention
- Simulated checkout and polymorphic payment execution
"""

import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import login_required, current_user

from app.models.show import Show, ShowSeat
from app.models.booking import Booking
from app.services.booking_service import BookingService
from app.services.payment_service import PaymentService
from app.services.ticket_service import TicketService
from app.core.interfaces import PaymentMethod

booking_bp = Blueprint("booking", __name__)
booking_service = BookingService()


def get_or_create_session_id():
    if "session_tracking_id" not in session:
        session["session_tracking_id"] = str(uuid.uuid4())
    return session["session_tracking_id"]


@booking_bp.route("/show/<int:show_id>/seats")
def seat_selection(show_id: int):
    """Visual Cinema Seating Layout Screen."""
    show = Show.query.get_or_404(show_id)
    session_id = get_or_create_session_id()
    user_id = current_user.id if current_user.is_authenticated else None

    # Fetch seat layout
    layout_data = booking_service.get_show_seating_layout(
        show_id=show_id,
        current_user_id=user_id,
        session_id=session_id
    )

    return render_template(
        "booking/seats.html",
        show=show,
        layout_data=layout_data
    )


@booking_bp.route("/api/lock-seats", methods=["POST"])
def lock_seats():
    """API endpoint called asynchronously when customer clicks 'Proceed to Checkout'."""
    data = request.get_json() or {}
    show_id = data.get("show_id")
    seat_ids = data.get("seat_ids", [])  # list of show_seat_ids

    if not show_id or not seat_ids:
        return jsonify({"success": False, "message": "No seats specified."}), 400

    session_id = get_or_create_session_id()
    user_id = current_user.id if current_user.is_authenticated else 0

    success, message, total_price = booking_service.lock_seats_for_checkout(
        show_id=show_id,
        show_seat_ids=seat_ids,
        user_id=user_id,
        session_id=session_id
    )

    if not success:
        return jsonify({"success": False, "message": message}), 409

    # Store checkout context in session
    session["checkout_show_id"] = show_id
    session["checkout_seat_ids"] = seat_ids
    session["checkout_total"] = total_price

    return jsonify({
        "success": True,
        "message": message,
        "redirect_url": url_for("booking.checkout")
    })


@booking_bp.route("/checkout")
@login_required
def checkout():
    """Review Order & Select Payment Method."""
    show_id = session.get("checkout_show_id")
    seat_ids = session.get("checkout_seat_ids", [])
    total_price = session.get("checkout_total", 0.0)

    if not show_id or not seat_ids:
        flash("Your checkout session has expired. Please select your seats again.", "warning")
        return redirect(url_for("main.index"))

    show = Show.query.get_or_404(show_id)
    seats = ShowSeat.query.filter(ShowSeat.id.in_(seat_ids)).all()

    return render_template(
        "booking/checkout.html",
        show=show,
        seats=seats,
        total_price=total_price,
        user=current_user
    )


@booking_bp.route("/process-payment", methods=["POST"])
@login_required
def process_payment():
    """Processes simulated payment polymorphically."""
    show_id = session.get("checkout_show_id")
    seat_ids = session.get("checkout_seat_ids", [])
    payment_method = request.form.get("payment_method", "UPI")

    if not show_id or not seat_ids:
        flash("Checkout session expired.", "danger")
        return redirect(url_for("main.index"))

    session_id = get_or_create_session_id()

    # 1. Confirm Booking & Commit Seats
    try:
        booking = booking_service.confirm_booking(
            show_id=show_id,
            show_seat_ids=seat_ids,
            user_id=current_user.id,
            session_id=session_id
        )
    except Exception as e:
        flash(f"Booking confirmation failed: {str(e)}", "danger")
        return redirect(url_for("booking.seat_selection", show_id=show_id))

    # 2. Gather Payment Payload for polymorphic processing
    payment_payload = {}
    if payment_method == "UPI":
        payment_payload["upi_id"] = request.form.get("upi_id", "user@okaxis")
    elif payment_method == "CARD":
        payment_payload["card_number"] = request.form.get("card_number", "4111111111111111")
        payment_payload["card_holder"] = request.form.get("card_holder", current_user.name)
        payment_payload["expiry"] = request.form.get("expiry", "12/28")
        payment_payload["cvv"] = request.form.get("cvv", "123")
    elif payment_method == "CASH":
        payment_payload["counter_id"] = "BOX_OFFICE_WEB"

    # 3. Polymorphic Payment Processing
    success, msg, payment_record = PaymentService.process_booking_payment(
        booking_id=booking.id,
        method=payment_method,
        payment_payload=payment_payload
    )

    if not success:
        flash(f"Payment simulation failed: {msg}", "danger")
        return redirect(url_for("booking.checkout"))

    # 4. Generate Digital Ticket & QR Code
    TicketService.generate_ticket(booking)

    # Clear checkout session
    session.pop("checkout_show_id", None)
    session.pop("checkout_seat_ids", None)
    session.pop("checkout_total", None)

    flash("Payment successful! Your tickets have been confirmed.", "success")
    return redirect(url_for("booking.success", booking_ref=booking.booking_reference))


@booking_bp.route("/success/<booking_ref>")
@login_required
def success(booking_ref: str):
    """Booking Success Page."""
    booking = Booking.query.filter_by(booking_reference=booking_ref).first_or_404()
    return render_template("booking/success.html", booking=booking)


@booking_bp.route("/cancel/<int:booking_id>", methods=["POST"])
@login_required
def cancel(booking_id: int):
    """Customer Booking Cancellation."""
    success, msg = booking_service.cancel_booking(booking_id=booking_id, user_id=current_user.id)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("auth.profile"))
