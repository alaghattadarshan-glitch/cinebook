package com.cinebook.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "bookings")
public class Booking {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 64)
    private String bookingReference;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "show_id", nullable = false)
    private Show show;

    private String customerName;
    private String customerEmail;
    private String customerPhone;

    @Column(nullable = false)
    private double totalAmount;

    @Column(nullable = false, length = 20)
    private String status = "CONFIRMED"; // PENDING, CONFIRMED, CANCELLED

    private String paymentMethod;
    private String transactionId;

    @Column(nullable = false)
    private LocalDateTime bookingTime = LocalDateTime.now();

    @OneToMany(mappedBy = "booking", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<BookingSeat> bookingSeats = new ArrayList<>();

    @OneToOne(mappedBy = "booking", cascade = CascadeType.ALL, orphanRemoval = true)
    private Ticket ticket;

    public Booking() {
        this.bookingReference = "CNB-BLR-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        this.bookingTime = LocalDateTime.now();
    }

    public Booking(Show show, String customerName, String customerEmail, String customerPhone, double totalAmount, String paymentMethod, String transactionId) {
        this();
        this.show = show;
        this.customerName = customerName;
        this.customerEmail = customerEmail;
        this.customerPhone = customerPhone;
        this.totalAmount = totalAmount;
        this.paymentMethod = paymentMethod;
        this.transactionId = transactionId;
        this.status = "CONFIRMED";
    }

    public Long getId() { return id; }
    public String getBookingReference() { return bookingReference; }
    public Show getShow() { return show; }
    public String getCustomerName() { return customerName; }
    public String getCustomerEmail() { return customerEmail; }
    public String getCustomerPhone() { return customerPhone; }
    public double getTotalAmount() { return totalAmount; }
    public String getStatus() { return status; }
    public String getPaymentMethod() { return paymentMethod; }
    public String getTransactionId() { return transactionId; }
    public LocalDateTime getBookingTime() { return bookingTime; }
    public List<BookingSeat> getBookingSeats() { return bookingSeats; }
    public Ticket getTicket() { return ticket; }
    public void setTicket(Ticket ticket) { this.ticket = ticket; }

    public String getSeatCodesFormatted() {
        return bookingSeats.stream()
                .map(BookingSeat::getSeatCode)
                .reduce((a, b) -> a + ", " + b)
                .orElse("None");
    }
}
