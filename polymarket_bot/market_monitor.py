"""
Market Monitoring Engine
Watches BTC 15m markets and tracks price movements
"""

import asyncio
import logging
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
from collections import deque

import config
from polymarket_client import PolymarketClient

logger = logging.getLogger(__name__)


class MarketData:
    """Stores market data and price history"""

    def __init__(self, market_id: str, token_id_yes: str, token_id_no: str):
        self.market_id = market_id
        self.token_id_yes = token_id_yes
        self.token_id_no = token_id_no

        self.yes_prices = deque(maxlen=config.PRICE_HISTORY_SIZE)
        self.no_prices = deque(maxlen=config.PRICE_HISTORY_SIZE)

        self.current_yes_bid: Optional[Decimal] = None
        self.current_yes_ask: Optional[Decimal] = None
        self.current_no_bid: Optional[Decimal] = None
        self.current_no_ask: Optional[Decimal] = None

        self.liquidity: Decimal = Decimal('0')
        self.last_update: Optional[datetime] = None

    def update_prices(
        self,
        yes_bid: Optional[Decimal],
        yes_ask: Optional[Decimal],
        no_bid: Optional[Decimal],
        no_ask: Optional[Decimal]
    ):
        """Update current prices and add to history"""
        self.current_yes_bid = yes_bid
        self.current_yes_ask = yes_ask
        self.current_no_bid = no_bid
        self.current_no_ask = no_ask

        if yes_bid and yes_ask:
            mid_yes = (yes_bid + yes_ask) / 2
            self.yes_prices.append(mid_yes)

        if no_bid and no_ask:
            mid_no = (no_bid + no_ask) / 2
            self.no_prices.append(mid_no)

        self.last_update = datetime.now()

    def get_price_volatility(self) -> Decimal:
        """Calculate price volatility based on recent history"""
        if len(self.yes_prices) < 10:
            return Decimal('0')

        yes_list = list(self.yes_prices)
        mean = sum(yes_list) / len(yes_list)

        variance = sum((x - mean) ** 2 for x in yes_list) / len(yes_list)
        std_dev = variance ** Decimal('0.5')

        return std_dev / mean if mean > 0 else Decimal('0')


class MarketMonitor:
    """Monitors markets and detects trading opportunities"""

    def __init__(self, client: PolymarketClient):
        self.client = client
        self.markets: Dict[str, MarketData] = {}
        self.running = False

    async def discover_btc_markets(self) -> List[Dict]:
        """
        Discover BTC 15-minute markets on Polymarket

        Returns:
            List of relevant market dictionaries
        """
        logger.info("Discovering BTC 15m markets...")

        markets = await self.client.get_markets(keywords=config.BTC_MARKET_KEYWORDS)

        relevant_markets = []
        for market in markets:
            # Check if market has sufficient volume
            volume = Decimal(str(market.get('volume', '0')))
            if volume >= config.MIN_MARKET_VOLUME:
                relevant_markets.append(market)

        logger.info(f"Found {len(relevant_markets)} relevant BTC 15m markets")
        return relevant_markets

    async def initialize_markets(self):
        """Initialize market tracking"""
        btc_markets = await self.discover_btc_markets()

        for market in btc_markets:
            market_id = market.get('id')
            # In Polymarket, binary markets have YES and NO tokens
            tokens = market.get('tokens', [])

            if len(tokens) >= 2:
                token_yes = tokens[0].get('token_id')
                token_no = tokens[1].get('token_id')

                market_data = MarketData(market_id, token_yes, token_no)
                self.markets[market_id] = market_data

                logger.info(f"Initialized market: {market.get('question')}")

    async def update_market_data(self, market_id: str):
        """
        Update market data for a specific market

        Args:
            market_id: The market ID to update
        """
        if market_id not in self.markets:
            return

        market_data = self.markets[market_id]

        try:
            # Get prices for YES token
            yes_bid, yes_ask = await self.client.get_best_prices(market_data.token_id_yes)

            # Get prices for NO token
            no_bid, no_ask = await self.client.get_best_prices(market_data.token_id_no)

            # Update market data
            market_data.update_prices(yes_bid, yes_ask, no_bid, no_ask)

            # Update liquidity
            yes_liquidity = await self.client.get_market_liquidity(market_data.token_id_yes)
            no_liquidity = await self.client.get_market_liquidity(market_data.token_id_no)
            market_data.liquidity = yes_liquidity + no_liquidity

        except Exception as e:
            logger.error(f"Error updating market {market_id}: {e}")

    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting market monitoring loop...")
        self.running = True

        while self.running:
            try:
                # Update all tracked markets
                for market_id in self.markets:
                    await self.update_market_data(market_id)

                # Wait before next update
                await asyncio.sleep(config.MARKET_CHECK_INTERVAL)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)

    def get_market_data(self, market_id: str) -> Optional[MarketData]:
        """Get market data for a specific market"""
        return self.markets.get(market_id)

    def get_all_markets(self) -> Dict[str, MarketData]:
        """Get all tracked markets"""
        return self.markets

    def stop(self):
        """Stop the monitoring loop"""
        logger.info("Stopping market monitor...")
        self.running = False
