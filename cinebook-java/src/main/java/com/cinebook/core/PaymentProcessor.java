package com.cinebook.core;

import java.time.LocalDateTime;

/**
 * Demonstrates:
 * 1. Abstraction: Contract defining payment behavior.
 * 2. Polymorphism: UPI, Card, and Cash process payments uniformly through this interface.
 */
public interface PaymentProcessor {
    PaymentResult processPayment(double amount, String details);
    boolean validatePaymentDetails(String details);
}
