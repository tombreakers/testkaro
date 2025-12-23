"""
Position Management and Exit Strategy
Actively manages open positions and determines when to exit
"""

import asyncio
import logging
from typing import Dict
from datetime import datetime

import config
from market_monitor import MarketMonitor, MarketData
from strategy import ArbitrageStrategy, SignalType
from executor import TradeExecutor, Position

logger = logging.getLogger(__name__)


class PositionManager:
    """Manages all active positions and determines exit timing"""

    def __init__(
        self,
        monitor: MarketMonitor,
        strategy: ArbitrageStrategy,
        executor: TradeExecutor
    ):
        self.monitor = monitor
        self.strategy = strategy
        self.executor = executor
        self.running = False

    async def evaluate_position_exit(self, position: Position) -> bool:
        """
        Evaluate if position should be exited

        Args:
            position: Position to evaluate

        Returns:
            True if position was closed, False otherwise
        """
        # Get current market data
        market_data = self.monitor.get_market_data(position.market_id)

        if not market_data:
            logger.warning(f"No market data for position {position.position_id}")
            return False

        # Check timeout
        if await self.executor.check_position_timeout(position):
            logger.warning(f"Position timeout, emergency closing {position.position_id}")
            await self.executor.emergency_close_position(position)
            return True

        # Generate exit signal
        exit_signal = self.strategy.generate_exit_signal(
            market_data,
            position.yes_entry_price,
            position.no_entry_price,
            position.entry_spread
        )

        # Execute exit if signal generated
        if exit_signal.signal_type == SignalType.EXIT:
            success = await self.executor.execute_exit_signal(exit_signal, position)
            if success:
                logger.info(f"Position exited successfully: {position.position_id}")
                return True
            else:
                logger.error(f"Failed to exit position: {position.position_id}")
                return False

        return False

    async def manage_positions_loop(self):
        """
        Main loop for managing active positions

        Continuously monitors all positions and exits them when appropriate
        """
        logger.info("Starting position management loop...")
        self.running = True

        while self.running:
            try:
                # Get all active positions
                positions = self.executor.get_active_positions()

                # Evaluate each position
                for position_id, position in list(positions.items()):
                    await self.evaluate_position_exit(position)

                # Wait before next evaluation
                await asyncio.sleep(config.MARKET_CHECK_INTERVAL)

            except Exception as e:
                logger.error(f"Error in position management loop: {e}")
                await asyncio.sleep(5)

    async def get_position_summary(self) -> Dict:
        """
        Get summary of all positions

        Returns:
            Dictionary with position statistics
        """
        positions = self.executor.get_active_positions()

        total_pnl = sum(p.pnl for p in positions.values())
        avg_hold_time = 0

        if positions:
            hold_times = [(datetime.now() - p.opened_at).total_seconds() for p in positions.values()]
            avg_hold_time = sum(hold_times) / len(hold_times)

        return {
            'active_positions': len(positions),
            'total_exposure': float(self.executor.get_total_exposure()),
            'total_pnl': float(total_pnl),
            'avg_hold_time': avg_hold_time
        }

    def stop(self):
        """Stop the position management loop"""
        logger.info("Stopping position manager...")
        self.running = False
