"""
Polymarket API Client Wrapper
Handles all interactions with Polymarket's CLOB (Central Limit Order Book)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.constants import POLYGON

import config

logger = logging.getLogger(__name__)


class PolymarketClient:
    """Wrapper for Polymarket CLOB client with trading functionality"""

    def __init__(self, private_key: str, chain_id: int = POLYGON):
        """
        Initialize Polymarket client

        Args:
            private_key: Ethereum private key for signing transactions
            chain_id: Blockchain chain ID (default: Polygon mainnet)
        """
        self.client = ClobClient(
            key=private_key,
            chain_id=chain_id,
            host="https://clob.polymarket.com"
        )
        self.active_positions: Dict[str, dict] = {}
        logger.info("Polymarket client initialized")

    async def get_markets(self, keywords: List[str] = None) -> List[Dict]:
        """
        Fetch markets from Polymarket

        Args:
            keywords: Filter markets by keywords

        Returns:
            List of market dictionaries
        """
        try:
            # Get all markets
            markets = self.client.get_markets()

            if keywords:
                # Filter markets by keywords
                filtered_markets = []
                for market in markets:
                    market_title = market.get('question', '').lower()
                    if any(keyword.lower() in market_title for keyword in keywords):
                        filtered_markets.append(market)
                return filtered_markets

            return markets
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []

    async def get_market_orderbook(self, token_id: str) -> Dict:
        """
        Get orderbook for a specific market token

        Args:
            token_id: The token ID to get orderbook for

        Returns:
            Orderbook dictionary with bids and asks
        """
        try:
            orderbook = self.client.get_order_book(token_id)
            return orderbook
        except Exception as e:
            logger.error(f"Error fetching orderbook for {token_id}: {e}")
            return {'bids': [], 'asks': []}

    async def get_best_prices(self, token_id: str) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """
        Get best bid and ask prices for a token

        Args:
            token_id: The token ID

        Returns:
            Tuple of (best_bid, best_ask) as Decimals
        """
        orderbook = await self.get_market_orderbook(token_id)

        best_bid = None
        best_ask = None

        if orderbook.get('bids') and len(orderbook['bids']) > 0:
            best_bid = Decimal(str(orderbook['bids'][0]['price']))

        if orderbook.get('asks') and len(orderbook['asks']) > 0:
            best_ask = Decimal(str(orderbook['asks'][0]['price']))

        return best_bid, best_ask

    async def get_market_liquidity(self, token_id: str) -> Decimal:
        """
        Calculate total liquidity in market

        Args:
            token_id: The token ID

        Returns:
            Total liquidity as Decimal
        """
        orderbook = await self.get_market_orderbook(token_id)

        total_liquidity = Decimal('0')

        for bid in orderbook.get('bids', []):
            total_liquidity += Decimal(str(bid['price'])) * Decimal(str(bid['size']))

        for ask in orderbook.get('asks', []):
            total_liquidity += Decimal(str(ask['price'])) * Decimal(str(ask['size']))

        return total_liquidity

    async def place_order(
        self,
        token_id: str,
        side: str,
        price: Decimal,
        size: Decimal,
        order_type: str = "GTC"
    ) -> Optional[Dict]:
        """
        Place an order on Polymarket

        Args:
            token_id: The token ID to trade
            side: "BUY" or "SELL"
            price: Price per share (0.01 to 0.99)
            size: Number of shares
            order_type: Order type (GTC, FOK, etc.)

        Returns:
            Order result dictionary or None if failed
        """
        try:
            if config.DRY_RUN:
                logger.info(f"[DRY RUN] Would place {side} order: {size} @ {price} for {token_id}")
                return {
                    'orderId': f'dry_run_{datetime.now().timestamp()}',
                    'status': 'simulated',
                    'side': side,
                    'price': float(price),
                    'size': float(size)
                }

            # Create order arguments
            order_args = OrderArgs(
                price=float(price),
                size=float(size),
                side=side,
                token_id=token_id
            )

            # Submit order
            signed_order = self.client.create_order(order_args)
            result = self.client.post_order(signed_order, OrderType.GTC)

            logger.info(f"Order placed: {side} {size} @ {price} for {token_id}")
            return result

        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None

    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order

        Args:
            order_id: The order ID to cancel

        Returns:
            True if successful, False otherwise
        """
        try:
            if config.DRY_RUN:
                logger.info(f"[DRY RUN] Would cancel order: {order_id}")
                return True

            self.client.cancel_order(order_id)
            logger.info(f"Order cancelled: {order_id}")
            return True

        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False

    async def get_open_orders(self) -> List[Dict]:
        """
        Get all open orders

        Returns:
            List of open orders
        """
        try:
            orders = self.client.get_orders()
            return [o for o in orders if o.get('status') == 'OPEN']
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []

    async def get_balance(self) -> Decimal:
        """
        Get account balance (USDC on Polygon)

        Returns:
            Balance as Decimal
        """
        try:
            # This would need to query the blockchain for USDC balance
            # For now, return a placeholder
            logger.warning("Balance checking not fully implemented")
            return Decimal('10000')
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return Decimal('0')

    def track_position(self, position_id: str, position_data: dict):
        """Track an active position"""
        self.active_positions[position_id] = {
            **position_data,
            'opened_at': datetime.now()
        }
        logger.info(f"Tracking position: {position_id}")

    def close_position(self, position_id: str):
        """Close and remove a tracked position"""
        if position_id in self.active_positions:
            position = self.active_positions.pop(position_id)
            logger.info(f"Closed position: {position_id}")
            return position
        return None

    def get_active_positions(self) -> Dict[str, dict]:
        """Get all active positions"""
        return self.active_positions
