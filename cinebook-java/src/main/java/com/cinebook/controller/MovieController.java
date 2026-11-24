package com.cinebook.controller;

import com.cinebook.model.Movie;
import com.cinebook.model.Show;
import com.cinebook.model.Theatre;
import com.cinebook.repository.MovieRepository;
import com.cinebook.repository.ShowRepository;
import com.cinebook.repository.TheatreRepository;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;

@Controller
public class MovieController {

    private final MovieRepository movieRepo;
    private final TheatreRepository theatreRepo;
    private final ShowRepository showRepo;

    public MovieController(MovieRepository movieRepo, TheatreRepository theatreRepo, ShowRepository showRepo) {
        this.movieRepo = movieRepo;
        this.theatreRepo = theatreRepo;
        this.showRepo = showRepo;
    }

    @GetMapping("/")
    public String index(Model model) {
        List<Movie> nowShowing = movieRepo.findByCategory("NOW_SHOWING");
        List<Movie> topRated = movieRepo.findByCategory("TOP_RATED");
        List<Movie> trending = movieRepo.findByCategory("TRENDING");
        List<Theatre> theatres = theatreRepo.findByCityIgnoreCase("Bengaluru");

        Movie featured = nowShowing.isEmpty() ? null : nowShowing.get(0);

        model.addAttribute("nowShowing", nowShowing);
        model.addAttribute("topRated", topRated);
        model.addAttribute("trending", trending);
        model.addAttribute("theatres", theatres);
        model.addAttribute("featuredMovie", featured);
        model.addAttribute("selectedCity", "Bengaluru");

        return "index";
    }

    @GetMapping("/movie/{id}")
    public String movieDetails(@PathVariable Long id, Model model) {
        Movie movie = movieRepo.findById(id).orElseThrow();
        List<Show> shows = showRepo.findByMovieId(id);

        model.addAttribute("movie", movie);
        model.addAttribute("shows", shows);
        model.addAttribute("selectedCity", "Bengaluru");

        return "movie-details";
    }
}
