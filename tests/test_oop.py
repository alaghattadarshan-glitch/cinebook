"""
Tests for Core Object-Oriented Programming (OOP) Principles.
Verifies:
1. Encapsulation (Properties, Validation, Private Variables)
2. Inheritance (BaseUser -> Customer/Admin, BasePayment -> Upi/Card/Cash)
3. Polymorphism (process_payment, calculate_price)
4. Abstraction (PaymentProcessor, TicketPricingStrategy)
"""

import pytest
from datetime import datetime
from app.core.interfaces import PaymentProcessor, TicketPricingStrategy, SeatTier, PaymentMethod, PaymentStatus
from app.core.payment import BasePayment, UpiPayment, CardPayment, CashPayment, PaymentFactory
from app.core.pricing import StandardPricingStrategy, WeekendPricingStrategy, ReclinerLuxuryStrategy, PricingContext
from app.models.user import BaseUser, Customer, Admin


def test_encapsulation_user_password():
    """Verify encapsulation prevents reading plain password and ensures hashing."""
    user = Customer(name="Alice", email="alice@test.com", password="securepassword123")
    
    # Attempting to read password property raises AttributeError
    with pytest.raises(AttributeError):
        _ = user.password

    # Encapsulated verify_password check
    assert user.verify_password("securepassword123") is True
    assert user.verify_password("wrongpassword") is False


def test_encapsulation_payment_amount_validation():
    """Verify encapsulated amount setter rejects invalid and non-positive numbers."""
    upi = UpiPayment(amount=150.0, upi_id="alice@okaxis")
    assert upi.amount == 150.0

    # Changing amount to negative must raise ValueError
    with pytest.raises(ValueError):
        upi.amount = -50.0

    with pytest.raises(ValueError):
        upi.amount = 0


def test_inheritance_and_polymorphism_user_roles():
    """Verify BaseUser inheritance and polymorphic is_admin() behavior."""
    customer = Customer(name="Bob", email="bob@test.com", password="password123")
    admin = Admin(name="Charlie", email="charlie@test.com", password="password123")

    assert isinstance(customer, BaseUser)
    assert isinstance(admin, BaseUser)

    # Polymorphic method returns role-specific boolean
    assert customer.is_admin() is False
    assert admin.is_admin() is True


def test_abstraction_and_polymorphism_payments():
    """Verify PaymentProcessor interface implementation and polymorphic processing."""
    # 1. UPI Payment
    upi_proc: PaymentProcessor = UpiPayment(amount=250.0)
    upi_res = upi_proc.process_payment(amount=250.0, payment_data={"upi_id": "customer@paytm"})
    assert upi_res.success is True
    assert upi_res.payment_method == PaymentMethod.UPI
    assert "UPI-" in upi_res.transaction_id

    # 2. Card Payment
    card_proc: PaymentProcessor = CardPayment(amount=500.0)
    card_res = card_proc.process_payment(amount=500.0, payment_data={
        "card_number": "4111222233334444",
        "card_holder": "John Doe",
        "expiry": "11/28",
        "cvv": "999"
    })
    assert card_res.success is True
    assert card_res.payment_method == PaymentMethod.CARD
    assert "CARD-" in card_res.transaction_id

    # 3. Cash Payment
    cash_proc: PaymentProcessor = CashPayment(amount=100.0)
    cash_res = cash_proc.process_payment(amount=100.0, payment_data={"counter_id": "BOX_OFFICE_A"})
    assert cash_res.success is True
    assert cash_res.payment_method == PaymentMethod.CASH


def test_payment_factory():
    """Verify Factory Pattern produces correct polymorphic payment instance."""
    p1 = PaymentFactory.create_payment("UPI", 100.0, upi_id="user@bank")
    p2 = PaymentFactory.create_payment("CARD", 200.0, card_number="4111222233334444")
    p3 = PaymentFactory.create_payment("CASH", 300.0)

    assert isinstance(p1, UpiPayment)
    assert isinstance(p2, CardPayment)
    assert isinstance(p3, CashPayment)


def test_polymorphic_pricing_strategies():
    """Verify TicketPricingStrategy polymorphism."""
    base_price = 200.0
    weekday = datetime(2025, 6, 4, 18, 0)  # Wednesday
    weekend = datetime(2025, 6, 7, 18, 0)  # Saturday

    std_strategy = StandardPricingStrategy()
    weekend_strategy = WeekendPricingStrategy()
    luxury_strategy = ReclinerLuxuryStrategy()

    # Standard Strategy
    assert std_strategy.calculate_price(base_price, SeatTier.REGULAR, weekday) == 200.0
    assert std_strategy.calculate_price(base_price, SeatTier.PREMIUM, weekday) == 280.0
    assert std_strategy.calculate_price(base_price, SeatTier.RECLINER, weekday) == 400.0

    # Weekend Strategy on Saturday (+20% surge)
    assert weekend_strategy.calculate_price(base_price, SeatTier.REGULAR, weekend) == 240.0
    assert weekend_strategy.calculate_price(base_price, SeatTier.PREMIUM, weekend) == 336.0

    # Luxury Strategy
    assert luxury_strategy.calculate_price(base_price, SeatTier.RECLINER, weekday) == round((200.0 * 2.2) + 150.0, 2)
