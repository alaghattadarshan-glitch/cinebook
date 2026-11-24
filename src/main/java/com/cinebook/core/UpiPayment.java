package com.cinebook.core;

import java.time.LocalDateTime;

public class UpiPayment extends BasePayment {
    private String upiId;

    public UpiPayment(double amount, String upiId) {
        super(amount);
        this.upiId = upiId;
    }

    @Override
    public boolean validatePaymentDetails(String details) {
        String idToCheck = (details != null && !details.isBlank()) ? details : this.upiId;
        return idToCheck != null && idToCheck.matches("^[\\w.\\-_]{2,256}@[a-zA-Z]{2,64}$");
    }

    @Override
    public PaymentResult processPayment(double amount, String details) {
        String id = (details != null && !details.isBlank()) ? details : this.upiId;
        if (!validatePaymentDetails(id)) {
            this.status = "FAILED";
            return new PaymentResult(false, "", "Invalid UPI ID format: " + id, "UPI", amount, LocalDateTime.now());
        }
        this.amount = amount;
        this.transactionId = generateTransactionRef("UPI");
        this.status = "SUCCESS";
        return new PaymentResult(true, this.transactionId, "UPI payment completed via " + id, "UPI", amount, LocalDateTime.now());
    }
}
