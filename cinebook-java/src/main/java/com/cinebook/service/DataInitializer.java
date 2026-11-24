package com.cinebook.service;

import com.cinebook.model.*;
import com.cinebook.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.List;

@Component
public class DataInitializer implements CommandLineRunner {

    private final MovieRepository movieRepo;
    private final TheatreRepository theatreRepo;
    private final ScreenRepository screenRepo;
    private final ShowRepository showRepo;

    public DataInitializer(MovieRepository movieRepo, TheatreRepository theatreRepo, ScreenRepository screenRepo, ShowRepository showRepo) {
        this.movieRepo = movieRepo;
        this.theatreRepo = theatreRepo;
        this.screenRepo = screenRepo;
        this.showRepo = showRepo;
    }

    @Override
    public void run(String... args) {
        // Seed Blockbuster Movies (Highlighting Kannada and Indian Hits)
        Movie m1 = new Movie(
            "Premada Oorali",
            "The 2026 superhit Kannada musical romantic drama directed by Manoj Kumar. Starring Shree Raam, Thapaswini Poonacha, and Rangayana Raghu.",
            "/static/images/posters/premada_oorali.jpg",
            "/static/images/posters/premada_oorali.jpg",
            "2026-09-25", 8.9, "Romance, Musical, Drama", "Kannada", 142, "NOW_SHOWING"
        );
        Movie m2 = new Movie(
            "Ramayana: Part 1",
            "Nitesh Tiwari's epic adaptation starring Ranbir Kapoor as Lord Rama, Sai Pallavi as Sita, and Yash as Ravana in a monumental cinematic journey.",
            "/static/images/posters/ramayana.jpg",
            "/static/images/posters/ramayana.jpg",
            "2026-11-05", 9.4, "Mythology, Action, Epic", "Hindi / Kannada", 185, "NOW_SHOWING"
        );
        Movie m3 = new Movie(
            "Kantara: Chapter 1",
            "Rishab Shetty's epic folklore action drama exploring the sacred divine origins during the Kadamba dynasty.",
            "/static/images/posters/kantara.jpg",
            "/static/images/posters/kantara.jpg",
            "2025-10-02", 9.2, "Folklore, Action, Thriller", "Kannada", 150, "NOW_SHOWING"
        );
        Movie m4 = new Movie(
            "KGF: Chapter 2",
            "Rocking Star Yash's landmark blockbuster set in the gold fields of Kolar.",
            "/static/images/posters/kgf2.jpg",
            "/static/images/posters/kgf2.jpg",
            "2022-04-14", 8.8, "Action, Crime, Drama", "Kannada", 168, "TOP_RATED"
        );
        Movie m5 = new Movie(
            "Kalki 2898 AD",
            "Modern avatar of Vishnu descends to protect the dystopian world. Starring Prabhas, Amitabh Bachchan, Kamal Haasan.",
            "/static/images/posters/kalki.jpg",
            "/static/images/posters/kalki.jpg",
            "2024-06-27", 7.8, "Action, Sci-Fi", "Telugu / Kannada", 181, "TRENDING"
        );

        movieRepo.saveAll(List.of(m1, m2, m3, m4, m5));

        // Seed Iconic Bengaluru Theatres
        Theatre t1 = new Theatre("PVR Superplex - Forum South Bangalore", "Bengaluru", "Kanakapura Road, Konanakunte", "Forum South Mall, Bengaluru");
        Theatre t2 = new Theatre("INOX Megaplex - Mall of Asia", "Bengaluru", "Bellary Road, Byatarayanapura", "Phoenix Mall of Asia, Yelahanka");
        Theatre t3 = new Theatre("Urvashi Cinema - Iconic 4K RGB Laser", "Bengaluru", "Lalbagh Road, Sudhama Nagar", "58, Lalbagh Main Rd, Bengaluru");
        Theatre t4 = new Theatre("Cinepolis VIP - Nexus Shantiniketan", "Bengaluru", "Whitefield Main Road", "Nexus Mall, Whitefield, Bengaluru");

        theatreRepo.saveAll(List.of(t1, t2, t3, t4));

        Screen s1 = new Screen("Screen 1 - IMAX with Laser", "Dolby 12.1", "IMAX 3D", t1);
        Screen s2 = new Screen("Screen 1 - Insignia VIP", "Dolby Atmos", "Laser 4K", t2);
        Screen s3 = new Screen("Main Screen - Curved Laser", "Dolby Atmos 64", "4K RGB Laser", t3);
        Screen s4 = new Screen("Screen 1 - VIP Recliner", "Dolby 7.1", "VIP Luxury", t4);

        screenRepo.saveAll(List.of(s1, s2, s3, s4));

        LocalDateTime now = LocalDateTime.now();
        Show show1 = new Show(m1, s1, now.plusHours(2), now.plusHours(4).plusMinutes(22), 250.0);
        Show show2 = new Show(m2, s2, now.plusHours(3), now.plusHours(6).plusMinutes(5), 350.0);
        Show show3 = new Show(m1, s3, now.plusHours(5), now.plusHours(7).plusMinutes(22), 200.0);
        Show show4 = new Show(m3, s4, now.plusHours(4), now.plusHours(6).plusMinutes(30), 280.0);

        showRepo.saveAll(List.of(show1, show2, show3, show4));
        System.out.println("Java Cinebook Backend initialized with Bengaluru Theatres and Kannada Movies!");
    }
}
