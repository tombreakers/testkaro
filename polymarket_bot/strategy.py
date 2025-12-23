"""
Arbitrage Strategy - Gap Detection and Signal Generation
Detects price inefficiencies and generates trading signals
"""

import logging
from typing import Optional, Dict
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass

import config
from market_monitor import MarketData

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Trading signal types"""
    NONE = "NONE"
    ENTER_BOTH = "ENTER_BOTH"  # Enter both YES and NO sides
    EXIT = "EXIT"  # Exit position


@dataclass
class TradingSignal:
    """Represents a trading signal"""
    signal_type: SignalType
    market_id: str
    yes_price: Optional[Decimal] = None
    no_price: Optional[Decimal] = None
    spread: Optional[Decimal] = None
    confidence: float = 0.0
    reason: str = ""


class ArbitrageStrategy:
    """
    Arbitrage strategy based on mean reversion and gap trading

    The strategy works by:
    1. Detecting when YES/NO prices create inefficient spreads
    2. Entering both sides when spread widens beyond threshold
    3. Exiting when spread normalizes back
    """

    def __init__(self):
        self.min_spread = config.MIN_SPREAD
        self.target_spread = config.TARGET_SPREAD
        self.max_spread = config.MAX_SPREAD
        self.exit_spread = config.EXIT_SPREAD

    def calculate_spread(self, market_data: MarketData) -> Optional[Decimal]:
        """
        Calculate the price spread inefficiency

        In efficient markets: YES price + NO price ≈ 1.0
        When spread deviates significantly, there's an arbitrage opportunity

        Args:
            market_data: Market data object

        Returns:
            Spread as Decimal, or None if data insufficient
        """
        yes_ask = market_data.current_yes_ask
        no_ask = market_data.current_no_ask

        if not yes_ask or not no_ask:
            return None

        # Calculate how much the sum deviates from 1.0
        total = yes_ask + no_ask
        spread = abs(total - Decimal('1.0'))

        return spread

    def detect_gap(self, market_data: MarketData) -> bool:
        """
        Detect if one side is moving faster than the other

        This happens during news events when one side gets emotional buying

        Args:
            market_data: Market data object

        Returns:
            True if gap detected, False otherwise
        """
        if len(market_data.yes_prices) < 5 or len(market_data.no_prices) < 5:
            return False

        # Get recent price changes
        yes_recent = list(market_data.yes_prices)[-5:]
        no_recent = list(market_data.no_prices)[-5:]

        yes_change = (yes_recent[-1] - yes_recent[0]) / yes_recent[0] if yes_recent[0] > 0 else 0
        no_change = (no_recent[-1] - no_recent[0]) / no_recent[0] if no_recent[0] > 0 else 0

        # If one side is moving significantly faster, there's a gap
        change_diff = abs(yes_change - no_change)

        return change_diff > self.min_spread

    def check_liquidity(self, market_data: MarketData) -> bool:
        """
        Verify market has sufficient liquidity

        Args:
            market_data: Market data object

        Returns:
            True if liquidity is sufficient, False otherwise
        """
        return market_data.liquidity >= config.MIN_LIQUIDITY

    def check_volatility(self, market_data: MarketData) -> bool:
        """
        Check if volatility is within acceptable range

        Too much volatility = risky, might be market manipulation
        Too little volatility = no opportunities

        Args:
            market_data: Market data object

        Returns:
            True if volatility is acceptable, False otherwise
        """
        volatility = market_data.get_price_volatility()

        if volatility > config.VOLATILITY_THRESHOLD:
            logger.warning(f"Market {market_data.market_id} too volatile: {volatility}")
            return False

        return True

    def generate_entry_signal(self, market_data: MarketData) -> TradingSignal:
        """
        Generate entry signal for arbitrage opportunity

        Args:
            market_data: Market data object

        Returns:
            TradingSignal object
        """
        # Calculate spread
        spread = self.calculate_spread(market_data)

        if not spread:
            return TradingSignal(
                signal_type=SignalType.NONE,
                market_id=market_data.market_id,
                reason="Insufficient price data"
            )

        # Check if spread is too extreme (might be data error)
        if spread > self.max_spread:
            return TradingSignal(
                signal_type=SignalType.NONE,
                market_id=market_data.market_id,
                spread=spread,
                reason=f"Spread too large: {spread}"
            )

        # Check liquidity
        if not self.check_liquidity(market_data):
            return TradingSignal(
                signal_type=SignalType.NONE,
                market_id=market_data.market_id,
                reason=f"Insufficient liquidity: {market_data.liquidity}"
            )

        # Check volatility
        if not self.check_volatility(market_data):
            return TradingSignal(
                signal_type=SignalType.NONE,
                market_id=market_data.market_id,
                reason="Volatility out of range"
            )

        # Detect gap
        has_gap = self.detect_gap(market_data)

        # Entry condition: spread above minimum AND gap detected
        if spread >= self.min_spread and has_gap:
            confidence = min(float(spread / self.target_spread), 1.0)

            return TradingSignal(
                signal_type=SignalType.ENTER_BOTH,
                market_id=market_data.market_id,
                yes_price=market_data.current_yes_ask,
                no_price=market_data.current_no_ask,
                spread=spread,
                confidence=confidence,
                reason=f"Arbitrage opportunity: spread={spread}, gap detected"
            )

        return TradingSignal(
            signal_type=SignalType.NONE,
            market_id=market_data.market_id,
            spread=spread,
            reason="No opportunity detected"
        )

    def generate_exit_signal(
        self,
        market_data: MarketData,
        entry_yes_price: Decimal,
        entry_no_price: Decimal,
        entry_spread: Decimal
    ) -> TradingSignal:
        """
        Generate exit signal for existing position

        Exit conditions:
        1. Spread has normalized (fallen below exit threshold)
        2. Position has been held too long
        3. Loss exceeds stop loss threshold

        Args:
            market_data: Current market data
            entry_yes_price: Price entered on YES side
            entry_no_price: Price entered on NO side
            entry_spread: Spread at entry

        Returns:
            TradingSignal object
        """
        current_spread = self.calculate_spread(market_data)

        if not current_spread:
            return TradingSignal(
                signal_type=SignalType.NONE,
                market_id=market_data.market_id,
                reason="Insufficient data for exit evaluation"
            )

        # Exit condition 1: Spread normalized
        if current_spread <= self.exit_spread:
            return TradingSignal(
                signal_type=SignalType.EXIT,
                market_id=market_data.market_id,
                yes_price=market_data.current_yes_bid,
                no_price=market_data.current_no_bid,
                spread=current_spread,
                reason="Spread normalized - take profit"
            )

        # Exit condition 2: Spread widened further (cut loss)
        if current_spread > entry_spread * Decimal('1.5'):
            return TradingSignal(
                signal_type=SignalType.EXIT,
                market_id=market_data.market_id,
                yes_price=market_data.current_yes_bid,
                no_price=market_data.current_no_bid,
                spread=current_spread,
                reason="Spread widening - stop loss"
            )

        return TradingSignal(
            signal_type=SignalType.NONE,
            market_id=market_data.market_id,
            spread=current_spread,
            reason="Hold position"
        )

    def evaluate_market(self, market_data: MarketData) -> TradingSignal:
        """
        Evaluate market and generate appropriate signal

        Args:
            market_data: Market data object

        Returns:
            TradingSignal object
        """
        return self.generate_entry_signal(market_data)
