package com.cinebook.core;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Demonstrates:
 * 1. Inheritance: BasePayment -> UpiPayment, CardPayment, CashPayment
 * 2. Encapsulation: Protected properties, amount validation getters and setters
 */
public abstract class BasePayment implements PaymentProcessor {
    public static final String CURRENCY = "INR";

    protected double amount;
    protected String status;
    protected String transactionId;

    public BasePayment(double amount) {
        setAmount(amount);
        this.status = "INITIATED";
    }

    public double getAmount() {
        return amount;
    }

    public void setAmount(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Payment amount must be greater than zero.");
        }
        this.amount = amount;
    }

    public String getStatus() {
        return status;
    }

    public String getTransactionId() {
        return transactionId;
    }

    public static String generateTransactionRef(String prefix) {
        return prefix + "-" + System.currentTimeMillis() + "-" + UUID.randomUUID().toString().substring(0, 6).toUpperCase();
    }
}
