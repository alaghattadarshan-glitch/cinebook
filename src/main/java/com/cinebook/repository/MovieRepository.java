package com.cinebook.repository;

import com.cinebook.model.Movie;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface MovieRepository extends JpaRepository<Movie, Long> {
    List<Movie> findByCategory(String category);
    List<Movie> findByTitleContainingIgnoreCase(String title);
}
