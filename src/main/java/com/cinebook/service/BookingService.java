package com.cinebook.service;

import com.cinebook.core.*;
import com.cinebook.model.*;
import com.cinebook.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class BookingService {

    private final ShowSeatRepository showSeatRepo;
    private final BookingRepository bookingRepo;
    private final TicketRepository ticketRepo;
    private final QrCodeService qrCodeService;
    private final PricingStrategy pricingStrategy = new WeekendPricingStrategy();

    public BookingService(ShowSeatRepository showSeatRepo, BookingRepository bookingRepo,
                          TicketRepository ticketRepo, QrCodeService qrCodeService) {
        this.showSeatRepo = showSeatRepo;
        this.bookingRepo = bookingRepo;
        this.ticketRepo = ticketRepo;
        this.qrCodeService = qrCodeService;
    }

    public List<ShowSeat> getShowSeats(Long showId) {
        return showSeatRepo.findByShowId(showId);
    }

    public Map<String, List<ShowSeat>> getShowSeatsGroupedByRow(Long showId) {
        List<ShowSeat> list = showSeatRepo.findByShowId(showId);
        return list.stream()
                .sorted((a, b) -> {
                    int rowComp = a.getSeat().getSeatRow().compareTo(b.getSeat().getSeatRow());
                    if (rowComp != 0) return rowComp;
                    return Integer.compare(a.getSeat().getSeatNumber(), b.getSeat().getSeatNumber());
                })
                .collect(Collectors.groupingBy(ss -> ss.getSeat().getSeatRow()));
    }

    @Transactional
    public boolean lockSeats(Long showId, List<Long> showSeatIds, String sessionId) {
        List<ShowSeat> seats = showSeatRepo.findByIdIn(showSeatIds);
        for (ShowSeat ss : seats) {
            if (!ss.isAvailable(sessionId)) {
                return false;
            }
        }
        for (ShowSeat ss : seats) {
            ss.acquireLock(sessionId, 10);
        }
        showSeatRepo.saveAll(seats);
        return true;
    }

    public double calculateTotal(List<Long> showSeatIds) {
        List<ShowSeat> seats = showSeatRepo.findByIdIn(showSeatIds);
        return seats.stream().mapToDouble(ShowSeat::getPrice).sum();
    }

    @Transactional
    public Booking confirmBookingAndProcessPayment(
            Show show,
            List<Long> showSeatIds,
            String customerName,
            String customerEmail,
            String customerPhone,
            String paymentMethod,
            String paymentDetails
    ) {
        List<ShowSeat> seats = showSeatRepo.findByIdIn(showSeatIds);
        double totalAmount = seats.stream().mapToDouble(ShowSeat::getPrice).sum();

        // Polymorphic OOP payment processing
        PaymentProcessor processor = PaymentFactory.createProcessor(paymentMethod, totalAmount);
        PaymentResult result = processor.processPayment(totalAmount, paymentDetails);

        if (!result.success()) {
            throw new RuntimeException("Payment processing failed: " + result.message());
        }

        // Create booking
        Booking booking = new Booking(
                show,
                customerName,
                customerEmail,
                customerPhone,
                Math.round(totalAmount * 100.0) / 100.0,
                result.paymentMethod(),
                result.transactionId()
        );

        for (ShowSeat ss : seats) {
            BookingSeat bs = new BookingSeat(booking, ss.getSeat().getSeatCode(), ss.getSeat().getTier(), ss.getPrice());
            booking.getBookingSeats().add(bs);
            ss.confirmBooking();
        }

        bookingRepo.save(booking);
        showSeatRepo.saveAll(seats);

        // Generate verified QR code pass
        String qrPayload = String.format("CINEBOOK VERIFIED PASS\nRef: %s\nMovie: %s\nTheatre: %s\nSeats: %s\nAmount: INR %.2f\nTxn: %s",
                booking.getBookingReference(),
                show.getMovie().getTitle(),
                show.getScreen().getTheatre().getName(),
                booking.getSeatCodesFormatted(),
                booking.getTotalAmount(),
                booking.getTransactionId()
        );

        String qrBase64 = qrCodeService.generateQrCodeBase64(qrPayload, 200, 200);
        Ticket ticket = new Ticket(booking, qrBase64);
        booking.setTicket(ticket);
        ticketRepo.save(ticket);

        return booking;
    }
}
