package com.cinebook.core;

/**
 * Factory Design Pattern in Java:
 * Returns appropriate polymorphic PaymentProcessor implementation.
 */
public class PaymentFactory {
    public static PaymentProcessor createProcessor(String method, double amount) {
        if (method == null) {
            return new UpiPayment(amount, "user@okaxis");
        }
        return switch (method.toUpperCase()) {
            case "CARD" -> new CardPayment(amount, "");
            case "CASH" -> new CashPayment(amount, "BOX_OFFICE_BENGALURU");
            default -> new UpiPayment(amount, "");
        };
    }
}
