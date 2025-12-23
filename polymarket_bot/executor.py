"""
Order Execution and Position Management
Handles trade execution and position tracking
"""

import asyncio
import logging
from typing import Optional, Dict
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass
import uuid

import config
from polymarket_client import PolymarketClient
from strategy import TradingSignal, SignalType

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents an active trading position"""
    position_id: str
    market_id: str
    yes_token_id: str
    no_token_id: str

    yes_entry_price: Decimal
    no_entry_price: Decimal
    entry_spread: Decimal

    position_size: Decimal
    opened_at: datetime

    yes_order_id: Optional[str] = None
    no_order_id: Optional[str] = None

    pnl: Decimal = Decimal('0')
    status: str = "OPEN"  # OPEN, CLOSED, STOPPED


class TradeExecutor:
    """Executes trades and manages positions"""

    def __init__(self, client: PolymarketClient):
        self.client = client
        self.active_positions: Dict[str, Position] = {}
        self.total_exposure: Decimal = Decimal('0')

    async def execute_entry_signal(
        self,
        signal: TradingSignal,
        yes_token_id: str,
        no_token_id: str
    ) -> Optional[Position]:
        """
        Execute entry signal by placing orders on both sides

        Args:
            signal: Trading signal
            yes_token_id: YES token ID
            no_token_id: NO token ID

        Returns:
            Position object if successful, None otherwise
        """
        if signal.signal_type != SignalType.ENTER_BOTH:
            logger.warning("Signal is not an entry signal")
            return None

        # Check if we have room for more exposure
        if self.total_exposure + config.POSITION_SIZE > config.MAX_EXPOSURE:
            logger.warning(f"Max exposure reached: {self.total_exposure}/{config.MAX_EXPOSURE}")
            return None

        logger.info(f"Executing entry signal for {signal.market_id}")
        logger.info(f"Spread: {signal.spread}, Confidence: {signal.confidence}")

        # Calculate position size (shares to buy on each side)
        # For Polymarket, we buy shares at the ask price
        yes_shares = config.POSITION_SIZE / signal.yes_price
        no_shares = config.POSITION_SIZE / signal.no_price

        # Place YES order
        yes_order = await self.client.place_order(
            token_id=yes_token_id,
            side="BUY",
            price=signal.yes_price,
            size=yes_shares
        )

        if not yes_order:
            logger.error("Failed to place YES order")
            return None

        # Place NO order
        no_order = await self.client.place_order(
            token_id=no_token_id,
            side="BUY",
            price=signal.no_price,
            size=no_shares
        )

        if not no_order:
            logger.error("Failed to place NO order, cancelling YES order")
            await self.client.cancel_order(yes_order['orderId'])
            return None

        # Create position
        position_id = str(uuid.uuid4())
        position = Position(
            position_id=position_id,
            market_id=signal.market_id,
            yes_token_id=yes_token_id,
            no_token_id=no_token_id,
            yes_entry_price=signal.yes_price,
            no_entry_price=signal.no_price,
            entry_spread=signal.spread,
            position_size=config.POSITION_SIZE,
            opened_at=datetime.now(),
            yes_order_id=yes_order['orderId'],
            no_order_id=no_order['orderId']
        )

        # Track position
        self.active_positions[position_id] = position
        self.total_exposure += config.POSITION_SIZE

        logger.info(f"Position opened: {position_id}")
        logger.info(f"YES: {yes_shares} @ {signal.yes_price}")
        logger.info(f"NO: {no_shares} @ {signal.no_price}")

        return position

    async def execute_exit_signal(
        self,
        signal: TradingSignal,
        position: Position
    ) -> bool:
        """
        Execute exit signal by closing the position

        Args:
            signal: Exit signal
            position: Position to close

        Returns:
            True if successful, False otherwise
        """
        if signal.signal_type != SignalType.EXIT:
            logger.warning("Signal is not an exit signal")
            return False

        logger.info(f"Executing exit signal for position {position.position_id}")
        logger.info(f"Reason: {signal.reason}")

        # Calculate shares to sell (same as we bought)
        yes_shares = position.position_size / position.yes_entry_price
        no_shares = position.position_size / position.no_entry_price

        # Sell YES position
        yes_exit = await self.client.place_order(
            token_id=position.yes_token_id,
            side="SELL",
            price=signal.yes_price,
            size=yes_shares
        )

        # Sell NO position
        no_exit = await self.client.place_order(
            token_id=position.no_token_id,
            side="SELL",
            price=signal.no_price,
            size=no_shares
        )

        if not yes_exit or not no_exit:
            logger.error("Failed to exit position completely")
            return False

        # Calculate P&L
        yes_pnl = (signal.yes_price - position.yes_entry_price) * yes_shares
        no_pnl = (signal.no_price - position.no_entry_price) * no_shares
        total_pnl = yes_pnl + no_pnl

        position.pnl = total_pnl
        position.status = "CLOSED"

        # Update exposure
        self.total_exposure -= position.position_size

        logger.info(f"Position closed: {position.position_id}")
        logger.info(f"P&L: ${total_pnl:.2f}")

        # Remove from active positions
        if position.position_id in self.active_positions:
            del self.active_positions[position.position_id]

        return True

    async def check_position_timeout(self, position: Position) -> bool:
        """
        Check if position has been held too long

        Args:
            position: Position to check

        Returns:
            True if position should be closed, False otherwise
        """
        time_held = (datetime.now() - position.opened_at).total_seconds()

        if time_held > config.MAX_POSITION_TIME:
            logger.warning(f"Position {position.position_id} held too long: {time_held}s")
            return True

        return False

    async def emergency_close_position(self, position: Position):
        """
        Emergency close position at market prices

        Args:
            position: Position to close
        """
        logger.warning(f"Emergency closing position {position.position_id}")

        yes_shares = position.position_size / position.yes_entry_price
        no_shares = position.position_size / position.no_entry_price

        # Try to close at any price
        await self.client.place_order(
            token_id=position.yes_token_id,
            side="SELL",
            price=Decimal('0.01'),  # Sell at very low price to ensure fill
            size=yes_shares
        )

        await self.client.place_order(
            token_id=position.no_token_id,
            side="SELL",
            price=Decimal('0.01'),
            size=no_shares
        )

        position.status = "STOPPED"
        self.total_exposure -= position.position_size

        if position.position_id in self.active_positions:
            del self.active_positions[position.position_id]

    def get_active_positions(self) -> Dict[str, Position]:
        """Get all active positions"""
        return self.active_positions

    def get_total_exposure(self) -> Decimal:
        """Get total exposure"""
        return self.total_exposure

    def get_position_count(self) -> int:
        """Get number of active positions"""
        return len(self.active_positions)
