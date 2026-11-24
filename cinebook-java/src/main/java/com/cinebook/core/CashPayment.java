package com.cinebook.core;

import java.time.LocalDateTime;

public class CashPayment extends BasePayment {
    private String counterId;

    public CashPayment(double amount, String counterId) {
        super(amount);
        this.counterId = (counterId != null) ? counterId : "BOX_OFFICE_BENGALURU";
    }

    @Override
    public boolean validatePaymentDetails(String details) {
        return true;
    }

    @Override
    public PaymentResult processPayment(double amount, String details) {
        this.amount = amount;
        this.transactionId = generateTransactionRef("CASH");
        this.status = "SUCCESS";
        return new PaymentResult(true, this.transactionId, "Cash collected at Counter " + counterId, "CASH", amount, LocalDateTime.now());
    }
}
