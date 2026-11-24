package com.cinebook.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * Concurrency & Seat Locking model.
 * Tracks per-show seat states (AVAILABLE, LOCKED, BOOKED) with atomic timeout resolution.
 */
@Entity
@Table(name = "show_seats", uniqueConstraints = {
    @UniqueConstraint(columnNames = {"show_id", "seat_id"})
})
public class ShowSeat {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "show_id", nullable = false)
    private Show show;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "seat_id", nullable = false)
    private Seat seat;

    @Column(nullable = false)
    private double price;

    @Column(nullable = false, length = 20)
    private String status = "AVAILABLE"; // AVAILABLE, LOCKED, BOOKED

    private LocalDateTime lockedUntil;
    private String lockedBySessionId;

    public ShowSeat() {}

    public ShowSeat(Show show, Seat seat, double price) {
        this.show = show;
        this.seat = seat;
        this.price = price;
        this.status = "AVAILABLE";
    }

    public Long getId() { return id; }
    public Show getShow() { return show; }
    public Seat getSeat() { return seat; }
    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }
    public String getStatus() { return status; }
    public LocalDateTime getLockedUntil() { return lockedUntil; }
    public String getLockedBySessionId() { return lockedBySessionId; }

    public boolean isAvailable(String currentSessionId) {
        if ("BOOKED".equalsIgnoreCase(status)) {
            return false;
        }
        if ("LOCKED".equalsIgnoreCase(status)) {
            if (lockedUntil != null && LocalDateTime.now().isAfter(lockedUntil)) {
                return true; // Lock has expired automatically
            }
            return currentSessionId != null && currentSessionId.equals(lockedBySessionId);
        }
        return true;
    }

    public boolean acquireLock(String sessionId, int timeoutMinutes) {
        if (!isAvailable(sessionId)) {
            return false;
        }
        this.status = "LOCKED";
        this.lockedBySessionId = sessionId;
        this.lockedUntil = LocalDateTime.now().plusMinutes(timeoutMinutes);
        return true;
    }

    public void releaseLock() {
        if ("LOCKED".equalsIgnoreCase(status)) {
            this.status = "AVAILABLE";
            this.lockedBySessionId = null;
            this.lockedUntil = null;
        }
    }

    public void confirmBooking() {
        this.status = "BOOKED";
        this.lockedBySessionId = null;
        this.lockedUntil = null;
    }
}
