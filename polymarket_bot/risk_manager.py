"""
Risk Management and Safety Checks
Ensures the bot operates within safe parameters
"""

import logging
from typing import Optional
from decimal import Decimal
from datetime import datetime, timedelta

import config
from executor import TradeExecutor
from market_monitor import MarketData

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages trading risk and enforces safety limits"""

    def __init__(self, executor: TradeExecutor):
        self.executor = executor

        # Track performance
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = Decimal('0')

        # Circuit breaker
        self.daily_loss_limit = config.MAX_EXPOSURE * Decimal('0.2')  # 20% of max exposure
        self.daily_pnl = Decimal('0')
        self.last_reset = datetime.now()

        # Consecutive losses
        self.consecutive_losses = 0
        self.max_consecutive_losses = 5

        self.circuit_breaker_active = False

    def reset_daily_tracking(self):
        """Reset daily tracking metrics"""
        current_time = datetime.now()

        # Reset if it's a new day
        if (current_time - self.last_reset) > timedelta(days=1):
            logger.info("Resetting daily risk tracking")
            self.daily_pnl = Decimal('0')
            self.last_reset = current_time

    def check_exposure_limit(self) -> bool:
        """
        Check if we're within exposure limits

        Returns:
            True if safe to trade, False otherwise
        """
        current_exposure = self.executor.get_total_exposure()

        if current_exposure >= config.MAX_EXPOSURE:
            logger.warning(f"Exposure limit reached: {current_exposure}/{config.MAX_EXPOSURE}")
            return False

        return True

    def check_daily_loss_limit(self) -> bool:
        """
        Check if daily loss limit has been hit

        Returns:
            True if safe to trade, False otherwise
        """
        self.reset_daily_tracking()

        if self.daily_pnl <= -self.daily_loss_limit:
            logger.error(f"Daily loss limit hit: {self.daily_pnl}")
            self.activate_circuit_breaker("Daily loss limit exceeded")
            return False

        return True

    def check_consecutive_losses(self) -> bool:
        """
        Check for too many consecutive losses

        Returns:
            True if safe to trade, False otherwise
        """
        if self.consecutive_losses >= self.max_consecutive_losses:
            logger.error(f"Too many consecutive losses: {self.consecutive_losses}")
            self.activate_circuit_breaker("Consecutive losses threshold exceeded")
            return False

        return True

    def validate_trade_parameters(
        self,
        market_data: MarketData,
        position_size: Decimal
    ) -> tuple[bool, str]:
        """
        Validate trade parameters before execution

        Args:
            market_data: Market data for the trade
            position_size: Size of position to take

        Returns:
            Tuple of (is_valid, reason)
        """
        # Check liquidity
        if market_data.liquidity < config.MIN_LIQUIDITY:
            return False, f"Insufficient liquidity: {market_data.liquidity}"

        # Check position size
        if position_size <= 0:
            return False, "Invalid position size"

        if position_size > config.MAX_EXPOSURE:
            return False, "Position size exceeds max exposure"

        # Check price sanity
        if not market_data.current_yes_ask or not market_data.current_no_ask:
            return False, "Missing price data"

        if market_data.current_yes_ask <= 0 or market_data.current_yes_ask >= 1:
            return False, f"Invalid YES price: {market_data.current_yes_ask}"

        if market_data.current_no_ask <= 0 or market_data.current_no_ask >= 1:
            return False, f"Invalid NO price: {market_data.current_no_ask}"

        return True, "Valid"

    def can_open_new_position(self) -> tuple[bool, str]:
        """
        Check if it's safe to open a new position

        Returns:
            Tuple of (can_trade, reason)
        """
        # Check circuit breaker
        if self.circuit_breaker_active:
            return False, "Circuit breaker active"

        # Check exposure
        if not self.check_exposure_limit():
            return False, "Exposure limit reached"

        # Check daily loss
        if not self.check_daily_loss_limit():
            return False, "Daily loss limit hit"

        # Check consecutive losses
        if not self.check_consecutive_losses():
            return False, "Too many consecutive losses"

        return True, "Safe to trade"

    def record_trade_result(self, pnl: Decimal):
        """
        Record the result of a closed trade

        Args:
            pnl: Profit/loss from the trade
        """
        self.total_trades += 1
        self.total_pnl += pnl
        self.daily_pnl += pnl

        if pnl > 0:
            self.winning_trades += 1
            self.consecutive_losses = 0
            logger.info(f"Winning trade: ${pnl:.2f}")
        else:
            self.losing_trades += 1
            self.consecutive_losses += 1
            logger.warning(f"Losing trade: ${pnl:.2f}")

        # Log stats
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        logger.info(f"Stats - Trades: {self.total_trades}, Win Rate: {win_rate:.1f}%, Total P&L: ${self.total_pnl:.2f}")

    def activate_circuit_breaker(self, reason: str):
        """
        Activate circuit breaker to stop all trading

        Args:
            reason: Reason for activation
        """
        logger.critical(f"CIRCUIT BREAKER ACTIVATED: {reason}")
        self.circuit_breaker_active = True

    def deactivate_circuit_breaker(self):
        """Deactivate circuit breaker (manual override)"""
        logger.info("Circuit breaker deactivated")
        self.circuit_breaker_active = False
        self.consecutive_losses = 0

    def get_risk_metrics(self) -> dict:
        """
        Get current risk metrics

        Returns:
            Dictionary of risk metrics
        """
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0

        return {
            'circuit_breaker_active': self.circuit_breaker_active,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'total_pnl': float(self.total_pnl),
            'daily_pnl': float(self.daily_pnl),
            'consecutive_losses': self.consecutive_losses,
            'current_exposure': float(self.executor.get_total_exposure()),
            'max_exposure': float(config.MAX_EXPOSURE)
        }
