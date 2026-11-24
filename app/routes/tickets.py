"""
Ticket Routes: View, Download PDF, QR Verification.
"""

from flask import Blueprint, render_template, send_file, abort, Response, current_app
from flask_login import login_required, current_user
import io

from app.models.booking import Booking, Ticket
from app.services.ticket_service import TicketService

tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.route("/<string:booking_ref>")
def view(booking_ref: str):
    """Digital Ticket View."""
    booking = Booking.query.filter_by(booking_reference=booking_ref).first_or_404()
    if not booking.ticket:
        TicketService.generate_ticket(booking)
    return render_template("tickets/view.html", booking=booking)


@tickets_bp.route("/<string:booking_ref>/download")
def download_pdf(booking_ref: str):
    """Download Ticket as high quality PDF."""
    booking = Booking.query.filter_by(booking_reference=booking_ref).first_or_404()
    if not booking.ticket:
        TicketService.generate_ticket(booking)

    static_folder = current_app.static_folder or "app/static"
    pdf_bytes = TicketService.generate_ticket_pdf(booking, static_folder=static_folder)

    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment;filename=Ticket_{booking.booking_reference}.pdf"}
    )
