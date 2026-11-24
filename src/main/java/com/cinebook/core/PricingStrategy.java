package com.cinebook.core;

import java.time.DayOfWeek;
import java.time.LocalDateTime;

/**
 * Demonstrates:
 * 1. Abstraction (Pricing Strategy Interface)
 * 2. Polymorphism (Standard, Weekend, Luxury Recliner implementations)
 */
public interface PricingStrategy {
    double calculatePrice(double basePrice, String seatTier, LocalDateTime showTime);
}
