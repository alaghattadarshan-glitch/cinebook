package com.cinebook.model;

import jakarta.persistence.*;

@Entity
@Table(name = "movies")
public class Movie {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long tmdbId;
    private String title;
    @Column(length = 2000)
    private String description;
    private String posterPath;
    private String backdropPath;
    private String releaseDate;
    private double rating;
    private String genre;
    private String language;
    private int runtime;
    private String category; // NOW_SHOWING, TRENDING, TOP_RATED

    public Movie() {}

    public Movie(String title, String description, String posterPath, String backdropPath,
                 String releaseDate, double rating, String genre, String language, int runtime, String category) {
        this.title = title;
        this.description = description;
        this.posterPath = posterPath;
        this.backdropPath = backdropPath;
        this.releaseDate = releaseDate;
        this.rating = rating;
        this.genre = genre;
        this.language = language;
        this.runtime = runtime;
        this.category = category;
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public String getPosterPath() { return posterPath; }
    public String getBackdropPath() { return backdropPath; }
    public String getReleaseDate() { return releaseDate; }
    public double getRating() { return rating; }
    public String getGenre() { return genre; }
    public String getLanguage() { return language; }
    public int getRuntime() { return runtime; }
    public String getCategory() { return category; }
}
