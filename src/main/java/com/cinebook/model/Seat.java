package com.cinebook.model;

import jakarta.persistence.*;

@Entity
@Table(name = "seats", uniqueConstraints = {
    @UniqueConstraint(columnNames = {"screen_id", "seatRow", "seatNumber"})
})
public class Seat {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "screen_id", nullable = false)
    private Screen screen;

    @Column(nullable = false, length = 5)
    private String seatRow; // A, B, C...

    @Column(nullable = false)
    private int seatNumber; // 1, 2, 3...

    @Column(nullable = false, length = 20)
    private String tier; // REGULAR, PREMIUM, RECLINER

    public Seat() {}

    public Seat(Screen screen, String seatRow, int seatNumber, String tier) {
        this.screen = screen;
        this.seatRow = seatRow;
        this.seatNumber = seatNumber;
        this.tier = tier;
    }

    public Long getId() { return id; }
    public Screen getScreen() { return screen; }
    public String getSeatRow() { return seatRow; }
    public int getSeatNumber() { return seatNumber; }
    public String getTier() { return tier; }

    public String getSeatCode() {
        return seatRow + seatNumber;
    }
}
