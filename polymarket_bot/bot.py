"""
Polymarket Arbitrage Bot - Main Runner
Coordinates all components and runs the trading bot
"""

import asyncio
import logging
import signal
import sys
from decimal import Decimal

import config
from polymarket_client import PolymarketClient
from market_monitor import MarketMonitor
from strategy import ArbitrageStrategy, SignalType
from executor import TradeExecutor
from position_manager import PositionManager
from risk_manager import RiskManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class PolymarketBot:
    """Main bot orchestrator"""

    def __init__(self, private_key: str):
        """
        Initialize the Polymarket bot

        Args:
            private_key: Ethereum private key for trading
        """
        logger.info("Initializing Polymarket Arbitrage Bot...")

        if config.DRY_RUN:
            logger.warning("BOT RUNNING IN DRY RUN MODE - No real trades will be executed")

        # Initialize components
        self.client = PolymarketClient(private_key)
        self.monitor = MarketMonitor(self.client)
        self.strategy = ArbitrageStrategy()
        self.executor = TradeExecutor(self.client)
        self.risk_manager = RiskManager(self.executor)
        self.position_manager = PositionManager(self.monitor, self.strategy, self.executor)

        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received, stopping bot...")
        self.stop()

    async def initialize(self):
        """Initialize bot and discover markets"""
        logger.info("Discovering and initializing BTC 15m markets...")
        await self.monitor.initialize_markets()

        market_count = len(self.monitor.get_all_markets())
        logger.info(f"Monitoring {market_count} markets")

        if market_count == 0:
            logger.warning("No markets found! Bot may not find trading opportunities.")

    async def trading_loop(self):
        """
        Main trading loop

        Continuously evaluates markets and executes trades
        """
        logger.info("Starting trading loop...")

        while self.running:
            try:
                # Get all markets
                markets = self.monitor.get_all_markets()

                # Evaluate each market for trading opportunities
                for market_id, market_data in markets.items():
                    # Skip if no recent data
                    if not market_data.last_update:
                        continue

                    # Check if we can open new positions
                    can_trade, reason = self.risk_manager.can_open_new_position()
                    if not can_trade:
                        logger.debug(f"Cannot open new position: {reason}")
                        continue

                    # Generate signal
                    signal = self.strategy.evaluate_market(market_data)

                    # Execute entry signal
                    if signal.signal_type == SignalType.ENTER_BOTH:
                        # Validate trade parameters
                        is_valid, validation_msg = self.risk_manager.validate_trade_parameters(
                            market_data,
                            config.POSITION_SIZE
                        )

                        if not is_valid:
                            logger.debug(f"Trade validation failed: {validation_msg}")
                            continue

                        # Execute the trade
                        position = await self.executor.execute_entry_signal(
                            signal,
                            market_data.token_id_yes,
                            market_data.token_id_no
                        )

                        if position:
                            logger.info(f"New position opened: {position.position_id}")

                # Wait before next iteration
                await asyncio.sleep(config.MARKET_CHECK_INTERVAL)

            except Exception as e:
                logger.error(f"Error in trading loop: {e}", exc_info=True)
                await asyncio.sleep(5)

    async def status_loop(self):
        """
        Status reporting loop

        Periodically logs bot status
        """
        while self.running:
            try:
                # Get position summary
                summary = await self.position_manager.get_position_summary()

                # Get risk metrics
                risk_metrics = self.risk_manager.get_risk_metrics()

                # Log status
                logger.info("=" * 60)
                logger.info("BOT STATUS")
                logger.info(f"Active Positions: {summary['active_positions']}")
                logger.info(f"Total Exposure: ${summary['total_exposure']:.2f}")
                logger.info(f"Total P&L: ${risk_metrics['total_pnl']:.2f}")
                logger.info(f"Win Rate: {risk_metrics['win_rate']:.1f}%")
                logger.info(f"Circuit Breaker: {'ACTIVE' if risk_metrics['circuit_breaker_active'] else 'Inactive'}")
                logger.info("=" * 60)

                # Wait 60 seconds before next status
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Error in status loop: {e}")
                await asyncio.sleep(60)

    async def run(self):
        """Run the bot"""
        try:
            # Initialize
            await self.initialize()

            logger.info("Starting bot components...")
            self.running = True

            # Start all loops concurrently
            await asyncio.gather(
                self.monitor.monitor_loop(),
                self.position_manager.manage_positions_loop(),
                self.trading_loop(),
                self.status_loop()
            )

        except Exception as e:
            logger.critical(f"Fatal error in bot: {e}", exc_info=True)
            self.stop()

    def stop(self):
        """Stop the bot gracefully"""
        logger.info("Stopping bot...")
        self.running = False
        self.monitor.stop()
        self.position_manager.stop()

        # Log final stats
        risk_metrics = self.risk_manager.get_risk_metrics()
        logger.info("Final Statistics:")
        logger.info(f"Total Trades: {risk_metrics['total_trades']}")
        logger.info(f"Win Rate: {risk_metrics['win_rate']:.1f}%")
        logger.info(f"Total P&L: ${risk_metrics['total_pnl']:.2f}")

        logger.info("Bot stopped")


async def main():
    """Main entry point"""
    # Check for private key
    if not config.PRIVATE_KEY:
        logger.error("PRIVATE_KEY not set in environment variables!")
        logger.error("Please set PRIVATE_KEY environment variable")
        sys.exit(1)

    # Create and run bot
    bot = PolymarketBot(config.PRIVATE_KEY)

    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        bot.stop()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("POLYMARKET ARBITRAGE BOT")
    logger.info("=" * 60)

    asyncio.run(main())
