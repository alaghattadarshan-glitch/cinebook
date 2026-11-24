"""
OOP Abstraction & Strategy Pattern: Ticket Pricing.
Demonstrates:
- Strategy Pattern (Open/Closed Principle)
- Polymorphism: Standard, Weekend, and ReclinerLuxury pricing strategies
- Encapsulation: Pricing multipliers and base validation
"""

from datetime import datetime
from typing import Dict
from app.core.interfaces import TicketPricingStrategy, SeatTier


class StandardPricingStrategy(TicketPricingStrategy):
    """
    Standard Base Pricing Strategy.
    Applies flat tiered seat multipliers (Regular 1.0x, Premium 1.4x, Recliner 2.0x).
    """

    # Class Variable: Tier multipliers
    TIER_MULTIPLIERS: Dict[SeatTier, float] = {
        SeatTier.REGULAR: 1.0,
        SeatTier.PREMIUM: 1.4,
        SeatTier.RECLINER: 2.0
    }

    def calculate_price(self, base_price: float, seat_tier: SeatTier, show_datetime: datetime) -> float:
        """
        Polymorphism: Concrete implementation of calculate_price.
        """
        multiplier = self.TIER_MULTIPLIERS.get(seat_tier, 1.0)
        return round(base_price * multiplier, 2)


class WeekendPricingStrategy(TicketPricingStrategy):
    """
    Weekend Surge Pricing Strategy.
    Applies a 20% weekend surge factor for Friday, Saturday, and Sunday shows.
    Demonstrates Polymorphism and Open/Closed Principle.
    """

    WEEKEND_SURGE: float = 1.20  # +20% on weekends
    TIER_MULTIPLIERS: Dict[SeatTier, float] = {
        SeatTier.REGULAR: 1.0,
        SeatTier.PREMIUM: 1.4,
        SeatTier.RECLINER: 2.0
    }

    def calculate_price(self, base_price: float, seat_tier: SeatTier, show_datetime: datetime) -> float:
        tier_mult = self.TIER_MULTIPLIERS.get(seat_tier, 1.0)
        # Saturday is 5, Sunday is 6, Friday is 4
        is_weekend = show_datetime.weekday() in (4, 5, 6)
        day_factor = self.WEEKEND_SURGE if is_weekend else 1.0
        return round(base_price * tier_mult * day_factor, 2)


class ReclinerLuxuryStrategy(TicketPricingStrategy):
    """
    Luxury Experience Pricing Strategy (for Dolby Atmos / IMAX Screens).
    Provides complimentary concessions baked into recliner tickets.
    """

    CONCESSION_SURCHARGE: float = 150.0  # Gourmet popcorn/beverage included

    def calculate_price(self, base_price: float, seat_tier: SeatTier, show_datetime: datetime) -> float:
        if seat_tier == SeatTier.RECLINER:
            return round((base_price * 2.2) + self.CONCESSION_SURCHARGE, 2)
        elif seat_tier == SeatTier.PREMIUM:
            return round(base_price * 1.5, 2)
        return round(base_price * 1.1, 2)


class PricingContext:
    """
    Context class for Strategy Pattern.
    Demonstrates:
    - Composition: Aggregates a TicketPricingStrategy instance
    - Dependency Injection: Can swap strategies dynamically at runtime
    """

    def __init__(self, strategy: TicketPricingStrategy = None):
        # Default to standard strategy
        self._strategy: TicketPricingStrategy = strategy or StandardPricingStrategy()

    @property
    def strategy(self) -> TicketPricingStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, new_strategy: TicketPricingStrategy) -> None:
        if not isinstance(new_strategy, TicketPricingStrategy):
            raise TypeError("Strategy must implement TicketPricingStrategy interface.")
        self._strategy = new_strategy

    def get_price(self, base_price: float, seat_tier: SeatTier, show_datetime: datetime) -> float:
        """Delegates price computation polymorphically to current strategy."""
        return self._strategy.calculate_price(base_price, seat_tier, show_datetime)
