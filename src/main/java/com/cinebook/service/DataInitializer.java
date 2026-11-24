package com.cinebook.service;

import com.cinebook.model.*;
import com.cinebook.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Component
public class DataInitializer implements CommandLineRunner {

    private final MovieRepository movieRepo;
    private final TheatreRepository theatreRepo;
    private final ScreenRepository screenRepo;
    private final SeatRepository seatRepo;
    private final ShowRepository showRepo;
    private final ShowSeatRepository showSeatRepo;

    public DataInitializer(MovieRepository movieRepo, TheatreRepository theatreRepo, ScreenRepository screenRepo,
                           SeatRepository seatRepo, ShowRepository showRepo, ShowSeatRepository showSeatRepo) {
        this.movieRepo = movieRepo;
        this.theatreRepo = theatreRepo;
        this.screenRepo = screenRepo;
        this.seatRepo = seatRepo;
        this.showRepo = showRepo;
        this.showSeatRepo = showSeatRepo;
    }

    @Override
    public void run(String... args) {
        // 1. Seed Blockbuster Movies (Highlighting Premada Oorali & Indian Cinema)
        Movie m1 = new Movie(
            "Premada Oorali",
            "The 2026 superhit Kannada musical romantic drama directed by Manoj Kumar. Starring Shree Raam, Thapaswini Poonacha, Ramika Shivu, and Rangayana Raghu. A scenic romantic musical celebrating Karnataka's heritage.",
            "/images/posters/premada_oorali.jpg",
            "/images/posters/premada_oorali.jpg",
            "2026-09-25", 8.9, "Romance, Musical, Drama", "Kannada", 142, "NOW_SHOWING"
        );
        Movie m2 = new Movie(
            "Ramayana: Part 1",
            "Nitesh Tiwari's epic adaptation of the timeless Indian saga. Starring Ranbir Kapoor as Lord Rama, Sai Pallavi as Sita, Yash as Ravana, and Ravie Dubey as Lakshman.",
            "/images/posters/ramayana.jpg",
            "/images/posters/ramayana.jpg",
            "2026-11-05", 9.4, "Mythology, Action, Epic", "Hindi / Kannada", 185, "NOW_SHOWING"
        );
        Movie m3 = new Movie(
            "Pushpa 2: The Rule",
            "The monumental clash continues. Allu Arjun reprises his iconic role alongside Fahadh Faasil and Rashmika Mandanna in Sukumar's pan-India action spectacle.",
            "/images/posters/pushpa2.jpg",
            "/images/posters/pushpa2.jpg",
            "2024-12-05", 9.1, "Action, Crime, Thriller", "Telugu / Kannada", 200, "NOW_SHOWING"
        );
        Movie m4 = new Movie(
            "Kantara: Chapter 1",
            "The legend returns with Rishab Shetty. Set during the reign of the Kadamba dynasty, this epic folklore action drama explores the sacred origins of Panjurli and Guliga Daiva.",
            "/images/posters/kantara.jpg",
            "/images/posters/kantara.jpg",
            "2025-10-02", 9.2, "Folklore, Action, Thriller", "Kannada", 150, "NOW_SHOWING"
        );
        Movie m5 = new Movie(
            "KGF: Chapter 2",
            "The blood-soaked land of Kolar Gold Fields has a new overlord now - Rocky. Starring Rocking Star Yash, Sanjay Dutt, and Raveena Tandon.",
            "/images/posters/kgf2.jpg",
            "/images/posters/kgf2.jpg",
            "2022-04-14", 8.8, "Action, Crime, Drama", "Kannada", 168, "TOP_RATED"
        );
        Movie m6 = new Movie(
            "Kalki 2898 AD",
            "Set in a post-apocalyptic world in the year 2898 AD, a modern-day avatar of Vishnu descends to protect the world. Starring Prabhas, Amitabh Bachchan, Kamal Haasan.",
            "/images/posters/kalki.jpg",
            "/images/posters/kalki.jpg",
            "2024-06-27", 7.8, "Action, Sci-Fi", "Telugu / Kannada", 181, "TRENDING"
        );

        movieRepo.saveAll(List.of(m1, m2, m3, m4, m5, m6));

        // 2. Seed Iconic Bengaluru Theatres
        Theatre t1 = new Theatre("PVR Superplex - Forum South Bangalore", "Bengaluru", "Kanakapura Road, Konanakunte", "Forum South Mall, Bengaluru");
        Theatre t2 = new Theatre("INOX Megaplex - Mall of Asia", "Bengaluru", "Bellary Road, Byatarayanapura", "Phoenix Mall of Asia, Yelahanka");
        Theatre t3 = new Theatre("Urvashi Cinema - Iconic 4K RGB Laser", "Bengaluru", "Lalbagh Road, Sudhama Nagar", "58, Lalbagh Main Rd, Bengaluru");
        Theatre t4 = new Theatre("Cinepolis VIP - Nexus Shantiniketan", "Bengaluru", "Whitefield Main Road", "Nexus Mall, Whitefield, Bengaluru");

        theatreRepo.saveAll(List.of(t1, t2, t3, t4));

        Screen sc1 = new Screen("Screen 1 - IMAX with Laser", "Dolby 12.1", "IMAX 3D", t1);
        Screen sc2 = new Screen("Screen 1 - INOX Insignia", "Dolby Atmos", "Laser 4K", t2);
        Screen sc3 = new Screen("Main Screen - Curved Laser", "Dolby Atmos 64", "4K RGB Laser", t3);
        Screen sc4 = new Screen("Screen 1 - VIP Recliner", "Dolby 7.1", "VIP Luxury", t4);

        screenRepo.saveAll(List.of(sc1, sc2, sc3, sc4));

        // 3. Configure Physical Seat Matrix for Screens (Rows A-E, 8 seats per row = 40 seats each)
        List<Screen> allScreens = List.of(sc1, sc2, sc3, sc4);
        for (Screen screen : allScreens) {
            List<Seat> seats = new ArrayList<>();
            for (String row : List.of("A", "B", "C", "D", "E")) {
                String tier = (row.equals("A") || row.equals("B")) ? "RECLINER" :
                             (row.equals("C")) ? "PREMIUM" : "REGULAR";
                for (int num = 1; num <= 8; num++) {
                    seats.add(new Seat(screen, row, num, tier));
                }
            }
            seatRepo.saveAll(seats);
        }

        // 4. Create Active Shows with ShowSeats
        LocalDateTime now = LocalDateTime.now();
        Show s1 = new Show(m1, sc1, now.plusHours(2), now.plusHours(4).plusMinutes(22), 250.0);
        Show s2 = new Show(m2, sc2, now.plusHours(3), now.plusHours(6).plusMinutes(5), 350.0);
        Show s3 = new Show(m1, sc3, now.plusHours(5), now.plusHours(7).plusMinutes(22), 200.0);
        Show s4 = new Show(m3, sc1, now.plusHours(6), now.plusHours(9).plusMinutes(20), 320.0);
        Show s5 = new Show(m4, sc4, now.plusHours(4), now.plusHours(6).plusMinutes(30), 280.0);

        List<Show> shows = List.of(s1, s2, s3, s4, s5);
        showRepo.saveAll(shows);

        for (Show show : shows) {
            List<Seat> physicalSeats = seatRepo.findByScreenIdOrderBySeatRowAscSeatNumberAsc(show.getScreen().getId());
            List<ShowSeat> showSeats = new ArrayList<>();
            for (Seat seat : physicalSeats) {
                double mult = seat.getTier().equals("RECLINER") ? 2.0 :
                             seat.getTier().equals("PREMIUM") ? 1.4 : 1.0;
                double seatPrice = Math.round(show.getBasePrice() * mult * 100.0) / 100.0;
                showSeats.add(new ShowSeat(show, seat, seatPrice));
            }
            showSeatRepo.saveAll(showSeats);
        }

        System.out.println("Java Cinebook initialized with 6 movies, Bengaluru theatres, and complete seat inventories!");
    }
}
