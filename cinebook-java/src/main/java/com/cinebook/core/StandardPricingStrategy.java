package com.cinebook.core;

import java.time.DayOfWeek;
import java.time.LocalDateTime;

public class StandardPricingStrategy implements PricingStrategy {
    @Override
    public double calculatePrice(double basePrice, String seatTier, LocalDateTime showTime) {
        double multiplier = switch (seatTier.toUpperCase()) {
            case "RECLINER" -> 2.0;
            case "PREMIUM" -> 1.4;
            default -> 1.0;
        };
        return Math.round(basePrice * multiplier * 100.0) / 100.0;
    }
}
