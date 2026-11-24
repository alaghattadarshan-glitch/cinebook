package com.cinebook.repository;

import com.cinebook.model.Seat;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface SeatRepository extends JpaRepository<Seat, Long> {
    List<Seat> findByScreenIdOrderBySeatRowAscSeatNumberAsc(Long screenId);
}
