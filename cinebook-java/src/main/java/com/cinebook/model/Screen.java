package com.cinebook.model;

import jakarta.persistence.*;

@Entity
@Table(name = "screens")
public class Screen {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String screenNumber;
    private String soundType;
    private String screenType;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "theatre_id")
    private Theatre theatre;

    public Screen() {}

    public Screen(String screenNumber, String soundType, String screenType, Theatre theatre) {
        this.screenNumber = screenNumber;
        this.soundType = soundType;
        this.screenType = screenType;
        this.theatre = theatre;
    }

    public Long getId() { return id; }
    public String getScreenNumber() { return screenNumber; }
    public String getSoundType() { return soundType; }
    public String getScreenType() { return screenType; }
    public Theatre getTheatre() { return theatre; }
}
