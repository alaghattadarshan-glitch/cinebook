"""
Digital Ticket Generation & QR Code Verification Service.
Demonstrates:
- High resolution QR Code generation embedding cryptographic/verification payload
- Printable PDF generation using ReportLab
- Real-time digital ticket representation
"""

import os
import io
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.models.base import db
from app.models.booking import Booking, Ticket


class TicketService:
    """Service handling digital ticket generation, QR encoding, and PDF rendering."""

    @staticmethod
    def generate_ticket(booking: Booking, static_folder: str = "app/static") -> Ticket:
        """
        Creates a Ticket record with a generated QR code image saved in static/tickets/.
        """
        if booking.ticket:
            return booking.ticket

        ticket_number = Ticket.generate_ticket_number()

        # Verification payload for scanning at theatre gate
        qr_payload = (
            f"CINEBOOK VERIFY\n"
            f"Ticket: {ticket_number}\n"
            f"Booking: {booking.booking_reference}\n"
            f"Movie: {booking.show.movie.title}\n"
            f"Theatre: {booking.show.theatre.name} - {booking.show.screen.screen_number}\n"
            f"Date: {booking.show.formatted_date} {booking.show.formatted_time}\n"
            f"Seats: {booking.seat_codes}\n"
            f"Amount: INR {booking.total_amount:.2f}\n"
            f"Status: VALID"
        )

        # Generate QR Code image
        qr_dir = os.path.join(static_folder, "tickets")
        os.makedirs(qr_dir, exist_ok=True)
        qr_filename = f"{ticket_number}.png"
        qr_file_path = os.path.join(qr_dir, qr_filename)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(qr_payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#e50914", back_color="#0b0f19")
        img.save(qr_file_path)

        # Create Ticket entity
        ticket = Ticket(
            ticket_number=ticket_number,
            booking_id=booking.id,
            qr_code_path=f"/static/tickets/{qr_filename}",
            qr_data=qr_payload,
            issued_at=datetime.utcnow()
        )
        db.session.add(ticket)
        db.session.commit()
        return ticket

    @staticmethod
    def generate_ticket_pdf(booking: Booking, static_folder: str = "app/static") -> bytes:
        """
        Generates a PDF ticket using ReportLab.
        Returns the raw PDF bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CinebookTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#e50914"),
            spaceAfter=12
        )
        label_style = ParagraphStyle(
            "LabelStyle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#64748b")
        )
        value_style = ParagraphStyle(
            "ValueStyle",
            parent=styles["Normal"],
            fontSize=12,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold"
        )

        elements = []

        # Header
        elements.append(Paragraph("<b>CINEBOOK CINEMAS</b> - ADMIT ONE", title_style))
        elements.append(Spacer(1, 12))

        # Booking Details Table
        data = [
            [Paragraph("Movie", label_style), Paragraph(booking.show.movie.title, value_style)],
            [Paragraph("Booking ID", label_style), Paragraph(booking.booking_reference, value_style)],
            [Paragraph("Theatre", label_style), Paragraph(booking.show.theatre.name, value_style)],
            [Paragraph("Screen", label_style), Paragraph(booking.show.screen.screen_number, value_style)],
            [Paragraph("Show Date & Time", label_style), Paragraph(f"{booking.show.formatted_date} at {booking.show.formatted_time}", value_style)],
            [Paragraph("Seats", label_style), Paragraph(booking.seat_codes, value_style)],
            [Paragraph("Total Amount", label_style), Paragraph(f"INR {booking.total_amount:.2f} (Paid)", value_style)],
            [Paragraph("Status", label_style), Paragraph(booking.status, value_style)]
        ]

        table = Table(data, colWidths=[150, 350])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # QR Code inclusion if present
        if booking.ticket and booking.ticket.qr_code_path:
            full_qr_path = os.path.join(static_folder, "..", booking.ticket.qr_code_path.lstrip("/"))
            if os.path.exists(full_qr_path):
                elements.append(Paragraph("<b>Entry Verification QR Code:</b>", label_style))
                elements.append(Spacer(1, 6))
                elements.append(RLImage(full_qr_path, width=130, height=130))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
