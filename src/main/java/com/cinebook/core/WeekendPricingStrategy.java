package com.cinebook.core;

import java.time.DayOfWeek;
import java.time.LocalDateTime;

public class WeekendPricingStrategy implements PricingStrategy {
    @Override
    public double calculatePrice(double basePrice, String seatTier, LocalDateTime showTime) {
        double tierMult = switch (seatTier.toUpperCase()) {
            case "RECLINER" -> 2.0;
            case "PREMIUM" -> 1.4;
            default -> 1.0;
        };
        boolean isWeekend = showTime.getDayOfWeek() == DayOfWeek.FRIDAY ||
                            showTime.getDayOfWeek() == DayOfWeek.SATURDAY ||
                            showTime.getDayOfWeek() == DayOfWeek.SUNDAY;
        double surge = isWeekend ? 1.20 : 1.0;
        return Math.round(basePrice * tierMult * surge * 100.0) / 100.0;
    }
}
