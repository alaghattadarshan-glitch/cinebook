package com.cinebook.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "tickets")
public class Ticket {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 64)
    private String ticketNumber;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "booking_id", nullable = false)
    private Booking booking;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String qrBase64;

    private LocalDateTime issuedAt = LocalDateTime.now();

    public Ticket() {
        this.ticketNumber = "TKT-KA-" + UUID.randomUUID().toString().substring(0, 10).toUpperCase();
        this.issuedAt = LocalDateTime.now();
    }

    public Ticket(Booking booking, String qrBase64) {
        this();
        this.booking = booking;
        this.qrBase64 = qrBase64;
    }

    public Long getId() { return id; }
    public String getTicketNumber() { return ticketNumber; }
    public Booking getBooking() { return booking; }
    public String getQrBase64() { return qrBase64; }
    public LocalDateTime getIssuedAt() { return issuedAt; }
}
