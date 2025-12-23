"""
Configuration for Polymarket Arbitrage Bot
"""

import os
from decimal import Decimal

# Polymarket API Configuration
POLYMARKET_API_KEY = os.getenv('POLYMARKET_API_KEY', '')
POLYMARKET_SECRET = os.getenv('POLYMARKET_SECRET', '')
POLYMARKET_PASSPHRASE = os.getenv('POLYMARKET_PASSPHRASE', '')

# RPC endpoint for Polygon network (Polymarket runs on Polygon)
RPC_ENDPOINT = os.getenv('RPC_ENDPOINT', 'https://polygon-rpc.com')

# Private key for wallet (KEEP THIS SECRET!)
PRIVATE_KEY = os.getenv('PRIVATE_KEY', '')

# Trading Parameters
MAX_EXPOSURE = Decimal('25000')  # Maximum total exposure in USD
MIN_LIQUIDITY = Decimal('10000')  # Minimum liquidity required in market
ORDER_TIMEOUT = 15  # Seconds to wait for order execution
POSITION_SIZE = Decimal('120')  # Base position size in USD

# Arbitrage Strategy Parameters
MIN_SPREAD = Decimal('0.02')  # Minimum spread to trigger trade (2%)
TARGET_SPREAD = Decimal('0.05')  # Target spread for ideal entry (5%)
MAX_SPREAD = Decimal('0.15')  # Maximum spread (above this might be market issue)
EXIT_SPREAD = Decimal('0.01')  # Exit when spread narrows to this (1%)

# Risk Management
MAX_POSITION_TIME = 300  # Maximum time to hold position (seconds)
STOP_LOSS_PERCENT = Decimal('0.03')  # Stop loss at 3% loss
MIN_PROFIT_TARGET = Decimal('15')  # Minimum profit target per trade ($15)
MAX_PROFIT_TARGET = Decimal('70')  # Maximum profit target per trade ($70)

# Market Monitoring
MARKET_CHECK_INTERVAL = 1  # Seconds between market checks
PRICE_HISTORY_SIZE = 50  # Number of price points to keep in history
VOLATILITY_THRESHOLD = Decimal('0.10')  # Filter out extremely volatile periods

# BTC Market Configuration
BTC_MARKET_KEYWORDS = ['bitcoin', 'btc', '15m', '15 min']  # Keywords to identify BTC 15m markets
MIN_MARKET_VOLUME = Decimal('50000')  # Minimum market volume to consider

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'polymarket_bot.log'

# Safety Settings
DRY_RUN = os.getenv('DRY_RUN', 'True').lower() == 'true'  # Paper trading mode
ENABLE_NOTIFICATIONS = False  # Enable alerts (future feature)

# Fee Settings
TAKER_FEE = Decimal('0.0')  # Polymarket taker fee
MAKER_FEE = Decimal('0.0')  # Polymarket maker fee

# Performance Tracking
TRACK_PERFORMANCE = True
PERFORMANCE_FILE = 'performance.json'
