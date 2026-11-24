package com.cinebook.core;

import java.time.LocalDateTime;

public class CardPayment extends BasePayment {
    private String cardNumber;

    public CardPayment(double amount, String cardNumber) {
        super(amount);
        this.cardNumber = cardNumber;
    }

    @Override
    public boolean validatePaymentDetails(String details) {
        String card = (details != null && !details.isBlank()) ? details : this.cardNumber;
        return card != null && card.replaceAll("\\D", "").length() >= 15;
    }

    @Override
    public PaymentResult processPayment(double amount, String details) {
        if (!validatePaymentDetails(details)) {
            this.status = "FAILED";
            return new PaymentResult(false, "", "Invalid Card details", "CARD", amount, LocalDateTime.now());
        }
        this.amount = amount;
        this.transactionId = generateTransactionRef("CARD");
        this.status = "SUCCESS";
        String clean = (details != null) ? details.replaceAll("\\D", "") : "4111";
        String masked = "**** **** **** " + clean.substring(Math.max(0, clean.length() - 4));
        return new PaymentResult(true, this.transactionId, "Card authorized successfully: " + masked, "CARD", amount, LocalDateTime.now());
    }
}
