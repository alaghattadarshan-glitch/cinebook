package com.cinebook.core;

import java.time.LocalDateTime;

public record PaymentResult(
    boolean success,
    String transactionId,
    String message,
    String paymentMethod,
    double amount,
    LocalDateTime timestamp
) {}
