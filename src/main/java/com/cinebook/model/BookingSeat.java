package com.cinebook.model;

import jakarta.persistence.*;

@Entity
@Table(name = "booking_seats")
public class BookingSeat {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "booking_id", nullable = false)
    private Booking booking;

    @Column(nullable = false, length = 10)
    private String seatCode;

    @Column(nullable = false, length = 20)
    private String seatTier;

    @Column(nullable = false)
    private double price;

    public BookingSeat() {}

    public BookingSeat(Booking booking, String seatCode, String seatTier, double price) {
        this.booking = booking;
        this.seatCode = seatCode;
        this.seatTier = seatTier;
        this.price = price;
    }

    public Long getId() { return id; }
    public Booking getBooking() { return booking; }
    public String getSeatCode() { return seatCode; }
    public String getSeatTier() { return seatTier; }
    public double getPrice() { return price; }
}
