package com.cinebook.model;

import jakarta.persistence.*;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "theatres")
public class Theatre {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String city;
    private String location;
    private String address;

    @OneToMany(mappedBy = "theatre", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Screen> screens = new ArrayList<>();

    public Theatre() {}

    public Theatre(String name, String city, String location, String address) {
        this.name = name;
        this.city = city;
        this.location = location;
        this.address = address;
    }

    public Long getId() { return id; }
    public String getName() { return name; }
    public String getCity() { return city; }
    public String getLocation() { return location; }
    public String getAddress() { return address; }
    public List<Screen> getScreens() { return screens; }
}
