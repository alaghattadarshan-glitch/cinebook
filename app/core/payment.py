"""
OOP Polymorphism & Inheritance: Payment Processing Hierarchy.
Demonstrates:
- Inheritance: BasePayment -> UpiPayment, CardPayment, CashPayment
- Polymorphism: Overridden `process_payment` and `validate_payment_details`
- Encapsulation: Attribute access, validation of transaction details
- SOLID: Single Responsibility, Liskov Substitution (all subclasses substitute BasePayment seamlessly)
"""

import uuid
import re
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.interfaces import (
    PaymentProcessor,
    PaymentResult,
    PaymentMethod,
    PaymentStatus
)


class BasePayment(PaymentProcessor):
    """
    Abstract Base Class for all payment types.
    Demonstrates:
    - Inheritance: Serves as the parent class for concrete payment mechanisms.
    - Encapsulation: Protects internal transaction identifiers and amounts.
    - Class Variables & Static Methods: Reusable formatting and ID generation.
    """

    # Class Variable: System-wide currency standard
    CURRENCY: str = "INR"

    def __init__(self, amount: float):
        """
        Constructor (__init__) initializing protected instance variables.
        """
        # Encapsulation: Validating amount before assigning to private attribute
        self._amount: float = 0.0
        self.amount = amount  # Uses property setter for validation
        self._payment_method: PaymentMethod = PaymentMethod.CASH
        self._status: PaymentStatus = PaymentStatus.INITIATED
        self._transaction_id: Optional[str] = None
        self._created_at: datetime = datetime.utcnow()

    # Encapsulation with property getter and setter
    @property
    def amount(self) -> float:
        """Getter for payment amount."""
        return self._amount

    @amount.setter
    def amount(self, value: float) -> None:
        """Setter with validation: Amount must be strictly positive."""
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Payment amount must be a positive number greater than zero.")
        self._amount = round(float(value), 2)

    @property
    def payment_method(self) -> PaymentMethod:
        return self._payment_method

    @property
    def status(self) -> PaymentStatus:
        return self._status

    @property
    def transaction_id(self) -> Optional[str]:
        return self._transaction_id

    # Static Method: Generates standardized, unique transaction references
    @staticmethod
    def generate_transaction_ref(prefix: str = "TXN") -> str:
        """
        Static Method: Demonstrates static utility method that does not depend on instance state.
        """
        return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

    # Class Method: Alternative constructor (demonstrates Python's alternative to constructor overloading)
    @classmethod
    def create_for_amount(cls, amount: float):
        """
        Class Method: Factory method for creating an instance.
        """
        return cls(amount=amount)

    def __str__(self) -> str:
        return f"[{self._payment_method.value}] Amount: {self.CURRENCY} {self._amount:.2f} (Status: {self._status.value})"


class UpiPayment(BasePayment):
    """
    Concrete UPI Payment Implementation.
    Demonstrates:
    - Inheritance from BasePayment
    - Polymorphism: Custom UPI payment validation and processing logic
    """

    # Class variable: Regex pattern for valid VPA (Virtual Payment Address)
    VPA_PATTERN = re.compile(r"^[\w.\-_]{2,256}@[a-zA-Z]{2,64}$")

    def __init__(self, amount: float, upi_id: str = ""):
        super().__init__(amount=amount)
        self._payment_method = PaymentMethod.UPI
        self._upi_id: str = upi_id

    @property
    def upi_id(self) -> str:
        return self._upi_id

    @upi_id.setter
    def upi_id(self, value: str) -> None:
        if not self.validate_vpa(value):
            raise ValueError(f"Invalid UPI ID format: '{value}'. Expected format: user@bank")
        self._upi_id = value.strip()

    @classmethod
    def validate_vpa(cls, upi_id: str) -> bool:
        """Class method to validate Virtual Private Address pattern."""
        if not upi_id or not isinstance(upi_id, str):
            return False
        return bool(cls.VPA_PATTERN.match(upi_id.strip()))

    def validate_payment_details(self, payment_data: Dict[str, Any]) -> bool:
        """Method Overriding: UPI-specific validation."""
        upi_id = payment_data.get("upi_id") or self._upi_id
        return self.validate_vpa(upi_id)

    def process_payment(self, amount: float, payment_data: Dict[str, Any]) -> PaymentResult:
        """
        Polymorphism: Concrete implementation of process_payment for UPI.
        Simulates payment gateway integration (Google Pay, PhonePe, Paytm).
        """
        upi_id = payment_data.get("upi_id", self._upi_id)
        if not self.validate_vpa(upi_id):
            self._status = PaymentStatus.FAILED
            return PaymentResult(
                success=False,
                transaction_id="",
                message=f"Invalid UPI ID '{upi_id}'. Payment failed.",
                payment_method=PaymentMethod.UPI,
                amount=amount
            )

        # Simulation logic: simulate successful authorization
        self._amount = amount
        self._transaction_id = self.generate_transaction_ref(prefix="UPI")
        self._status = PaymentStatus.SUCCESS

        return PaymentResult(
            success=True,
            transaction_id=self._transaction_id,
            message=f"UPI Payment of INR {amount:.2f} successfully completed via {upi_id}.",
            payment_method=PaymentMethod.UPI,
            amount=amount
        )


class CardPayment(BasePayment):
    """
    Concrete Credit/Debit Card Payment Implementation.
    Demonstrates:
    - Inheritance from BasePayment
    - Polymorphism: Overridden card validation and tokenized payment processing
    - Data Masking & Encapsulation: Storing only masked card numbers for security
    """

    def __init__(self, amount: float, card_number: str = "", card_holder: str = "", expiry: str = "", cvv: str = ""):
        super().__init__(amount=amount)
        self._payment_method = PaymentMethod.CARD
        self._card_holder: str = card_holder
        self._masked_card: str = self.mask_card_number(card_number) if card_number else ""

    @property
    def card_holder(self) -> str:
        return self._card_holder

    @property
    def masked_card(self) -> str:
        return self._masked_card

    @staticmethod
    def mask_card_number(card_number: str) -> str:
        """Static method: Returns sanitized, masked card string (e.g., **** **** **** 1234)."""
        clean_num = re.sub(r"\D", "", card_number or "")
        if len(clean_num) >= 4:
            return f"**** **** **** {clean_num[-4:]}"
        return "**** **** **** ****"

    @staticmethod
    def luhn_checksum(card_number: str) -> bool:
        """Standard Luhn Algorithm validator for simulated card verification."""
        digits = [int(d) for d in re.sub(r"\D", "", card_number)]
        if len(digits) < 13 or len(digits) > 19:
            return False
        checksum = 0
        reverse_digits = digits[::-1]
        for i, digit in enumerate(reverse_digits):
            if i % 2 == 1:
                doubled = digit * 2
                checksum += (doubled - 9) if doubled > 9 else doubled
            else:
                checksum += digit
        return checksum % 10 == 0

    def validate_payment_details(self, payment_data: Dict[str, Any]) -> bool:
        """Method Overriding: Card-specific details validation."""
        card_num = re.sub(r"\D", "", str(payment_data.get("card_number", "")))
        expiry = str(payment_data.get("expiry", "")).strip()
        cvv = str(payment_data.get("cvv", "")).strip()

        # In simulation: accept valid length (15-16 digits) or Luhn match
        if len(card_num) not in (15, 16):
            return False
        if not re.match(r"^(0[1-9]|1[0-2])\/?([0-9]{2})$", expiry):
            return False
        if len(cvv) not in (3, 4):
            return False
        return True

    def process_payment(self, amount: float, payment_data: Dict[str, Any]) -> PaymentResult:
        """
        Polymorphism: Concrete implementation for Card transactions.
        Simulates Visa / Mastercard 3D Secure verification.
        """
        if not self.validate_payment_details(payment_data):
            self._status = PaymentStatus.FAILED
            return PaymentResult(
                success=False,
                transaction_id="",
                message="Card details validation failed. Please check Card Number, Expiry (MM/YY) and CVV.",
                payment_method=PaymentMethod.CARD,
                amount=amount
            )

        card_num = str(payment_data.get("card_number", ""))
        self._masked_card = self.mask_card_number(card_num)
        self._card_holder = payment_data.get("card_holder", "Cardholder")
        self._amount = amount
        self._transaction_id = self.generate_transaction_ref(prefix="CARD")
        self._status = PaymentStatus.SUCCESS

        return PaymentResult(
            success=True,
            transaction_id=self._transaction_id,
            message=f"Card Payment of INR {amount:.2f} authorized successfully ({self._masked_card}).",
            payment_method=PaymentMethod.CARD,
            amount=amount
        )


class CashPayment(BasePayment):
    """
    Concrete Cash / Counter Payment Implementation.
    Demonstrates:
    - Inheritance from BasePayment
    - Polymorphism: Counter authorization for Box Office or Admin desk bookings
    """

    def __init__(self, amount: float, counter_agent_id: str = "BOX_OFFICE_1"):
        super().__init__(amount=amount)
        self._payment_method = PaymentMethod.CASH
        self._counter_agent_id: str = counter_agent_id

    def validate_payment_details(self, payment_data: Dict[str, Any]) -> bool:
        """Method Overriding: Cash payments require counter verification."""
        return True

    def process_payment(self, amount: float, payment_data: Dict[str, Any]) -> PaymentResult:
        """
        Polymorphism: Concrete implementation for Box Office Cash.
        """
        self._amount = amount
        self._transaction_id = self.generate_transaction_ref(prefix="CASH")
        self._status = PaymentStatus.SUCCESS
        counter_id = payment_data.get("counter_id", self._counter_agent_id)

        return PaymentResult(
            success=True,
            transaction_id=self._transaction_id,
            message=f"Cash Payment of INR {amount:.2f} collected and verified at Counter ({counter_id}).",
            payment_method=PaymentMethod.CASH,
            amount=amount
        )


class PaymentFactory:
    """
    Factory Pattern: Creates the appropriate BasePayment subclass polymorphically.
    Demonstrates:
    - Factory Method Pattern
    - Open/Closed Principle
    """

    @staticmethod
    def create_payment(method: str, amount: float, **kwargs) -> BasePayment:
        """
        Returns a polymorphic instance of BasePayment depending on the selected method.
        """
        normalized = method.strip().upper()
        if normalized == PaymentMethod.UPI.value:
            return UpiPayment(amount=amount, upi_id=kwargs.get("upi_id", ""))
        elif normalized == PaymentMethod.CARD.value:
            return CardPayment(
                amount=amount,
                card_number=kwargs.get("card_number", ""),
                card_holder=kwargs.get("card_holder", ""),
                expiry=kwargs.get("expiry", ""),
                cvv=kwargs.get("cvv", "")
            )
        elif normalized == PaymentMethod.CASH.value:
            return CashPayment(
                amount=amount,
                counter_agent_id=kwargs.get("counter_id", "BOX_OFFICE_1")
            )
        else:
            raise ValueError(f"Unsupported payment method: '{method}'. Supported: UPI, CARD, CASH")
