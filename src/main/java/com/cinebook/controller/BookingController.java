package com.cinebook.controller;

import com.cinebook.model.*;
import com.cinebook.repository.*;
import com.cinebook.service.BookingService;
import jakarta.servlet.http.HttpSession;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@Controller
@RequestMapping("/book")
public class BookingController {

    private final ShowRepository showRepo;
    private final BookingRepository bookingRepo;
    private final BookingService bookingService;

    public BookingController(ShowRepository showRepo, BookingRepository bookingRepo, BookingService bookingService) {
        this.showRepo = showRepo;
        this.bookingRepo = bookingRepo;
        this.bookingService = bookingService;
    }

    private String getSessionId(HttpSession session) {
        String sessId = (String) session.getAttribute("CINEBOOK_SESSION_ID");
        if (sessId == null) {
            sessId = UUID.randomUUID().toString();
            session.setAttribute("CINEBOOK_SESSION_ID", sessId);
        }
        return sessId;
    }

    // 1. Seat Selection View
    @GetMapping("/show/{showId}/seats")
    public String selectSeats(@PathVariable Long showId, Model model, HttpSession session) {
        Show show = showRepo.findById(showId).orElseThrow();
        String sessionId = getSessionId(session);

        Map<String, List<ShowSeat>> layout = bookingService.getShowSeatsGroupedByRow(showId);

        model.addAttribute("show", show);
        model.addAttribute("layout", layout);
        model.addAttribute("sessionId", sessionId);

        return "seats";
    }

    // 2. Lock Seats REST API
    @PostMapping("/api/lock-seats")
    @ResponseBody
    public ResponseEntity<?> lockSeats(@RequestBody Map<String, Object> payload, HttpSession session) {
        Long showId = Long.valueOf(payload.get("showId").toString());
        List<?> seatIdsRaw = (List<?>) payload.get("seatIds");
        List<Long> seatIds = seatIdsRaw.stream().map(o -> Long.valueOf(o.toString())).toList();

        String sessionId = getSessionId(session);
        boolean locked = bookingService.lockSeats(showId, seatIds, sessionId);

        if (!locked) {
            return ResponseEntity.status(409).body(Map.of("success", false, "message", "One or more seats are already booked or reserved. Please choose different seats."));
        }

        double totalAmount = bookingService.calculateTotal(seatIds);
        session.setAttribute("CHECKOUT_SHOW_ID", showId);
        session.setAttribute("CHECKOUT_SEAT_IDS", seatIds);
        session.setAttribute("CHECKOUT_TOTAL", totalAmount);

        return ResponseEntity.ok(Map.of("success", true, "redirectUrl", "/book/checkout"));
    }

    // 3. Checkout Screen
    @GetMapping("/checkout")
    public String checkout(Model model, HttpSession session) {
        Long showId = (Long) session.getAttribute("CHECKOUT_SHOW_ID");
        @SuppressWarnings("unchecked")
        List<Long> seatIds = (List<Long>) session.getAttribute("CHECKOUT_SEAT_IDS");
        Double total = (Double) session.getAttribute("CHECKOUT_TOTAL");

        if (showId == null || seatIds == null || seatIds.isEmpty()) {
            return "redirect:/";
        }

        Show show = showRepo.findById(showId).orElseThrow();
        List<ShowSeat> selectedSeats = bookingService.getShowSeats(showId).stream()
                .filter(ss -> seatIds.contains(ss.getId()))
                .toList();

        model.addAttribute("show", show);
        model.addAttribute("seats", selectedSeats);
        model.addAttribute("totalPrice", total);

        return "checkout";
    }

    // 4. Payment Submission & Confirmation
    @PostMapping("/process-payment")
    public String processPayment(
            @RequestParam String customerName,
            @RequestParam String customerEmail,
            @RequestParam String customerPhone,
            @RequestParam String paymentMethod,
            @RequestParam(required = false, defaultValue = "") String upiId,
            @RequestParam(required = false, defaultValue = "") String cardNumber,
            HttpSession session,
            Model model
    ) {
        Long showId = (Long) session.getAttribute("CHECKOUT_SHOW_ID");
        @SuppressWarnings("unchecked")
        List<Long> seatIds = (List<Long>) session.getAttribute("CHECKOUT_SEAT_IDS");

        if (showId == null || seatIds == null || seatIds.isEmpty()) {
            return "redirect:/";
        }

        Show show = showRepo.findById(showId).orElseThrow();
        String paymentDetails = paymentMethod.equalsIgnoreCase("UPI") ? upiId : cardNumber;

        Booking booking = bookingService.confirmBookingAndProcessPayment(
                show,
                seatIds,
                customerName,
                customerEmail,
                customerPhone,
                paymentMethod,
                paymentDetails
        );

        // Clear checkout session
        session.removeAttribute("CHECKOUT_SHOW_ID");
        session.removeAttribute("CHECKOUT_SEAT_IDS");
        session.removeAttribute("CHECKOUT_TOTAL");

        return "redirect:/book/ticket/" + booking.getBookingReference();
    }

    // 5. Final Ticket View with QR Code and Admit-One Details
    @GetMapping("/ticket/{bookingRef}")
    public String viewTicket(@PathVariable String bookingRef, Model model) {
        Booking booking = bookingRepo.findByBookingReference(bookingRef).orElseThrow();
        model.addAttribute("booking", booking);
        return "ticket";
    }
}
