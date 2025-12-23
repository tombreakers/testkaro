# Polymarket Bot Troubleshooting Guide

## Issue: "No markets found" or "Found 0 relevant BTC 15m markets"

**Cause:** Polymarket may not have active BTC 15-minute markets at the moment, or the keywords don't match.

**Solutions:**

### 1. Check Polymarket manually
Visit https://polymarket.com/ and search for:
- "Bitcoin 15m"
- "BTC 15 min"
- Short-term Bitcoin price prediction markets

If no markets exist, the bot can't trade. These markets come and go.

### 2. Adjust search keywords

Edit `polymarket_bot/config.py`:
```python
# Try broader keywords
BTC_MARKET_KEYWORDS = ['bitcoin', 'btc']  # Remove '15m' requirement

# Or try different timeframes
BTC_MARKET_KEYWORDS = ['bitcoin', 'btc', '1h', '30m', '15m']
```

### 3. Lower volume requirement
```python
MIN_MARKET_VOLUME = Decimal('10000')  # Down from 50000
```

### 4. Trade different markets entirely

The strategy works on ANY binary prediction market with emotional overreactions. Try:
```python
# Sports events
MARKET_KEYWORDS = ['nba', 'basketball', 'score']

# Crypto markets
MARKET_KEYWORDS = ['ethereum', 'eth', 'bitcoin', 'btc']

# Politics (high volume)
MARKET_KEYWORDS = ['election', 'president', 'trump', 'biden']
```

---

## Issue: Bot places orders but they never fill

**Cause:** Prices move too fast, or liquidity is on the other side of the book.

**Solutions:**

### 1. Use market orders instead of limit orders

Edit `polymarket_bot/polymarket_client.py` at line ~130:

Currently it uses `OrderType.GTC` (Good Till Canceled limit orders).

You might need to adjust pricing to be more aggressive:
```python
# When buying YES, add slippage tolerance
adjusted_price = price * Decimal('1.01')  # Pay 1% more to ensure fill
```

### 2. Increase order timeout
In `config.py`:
```python
ORDER_TIMEOUT = 30  # Give orders more time to fill
```

### 3. Check if you have USDC

Your wallet needs USDC on Polygon, not ETH or MATIC.

Check balance:
```bash
# On your VPS, create a quick script
nano check_balance.py
```

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('YOUR_RPC_ENDPOINT'))
wallet = 'YOUR_WALLET_ADDRESS'

# USDC contract on Polygon
usdc_address = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'

# Standard ERC20 ABI (just balanceOf)
abi = [{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]

usdc = w3.eth.contract(address=usdc_address, abi=abi)
balance = usdc.functions.balanceOf(wallet).call()

print(f"USDC Balance: {balance / 1e6} USDC")  # USDC has 6 decimals
```

Run: `python check_balance.py`

---

## Issue: Positions stuck open, not exiting

**Cause:** Exit conditions too strict, or prices not normalizing.

**Solutions:**

### 1. Relax exit threshold
```python
EXIT_SPREAD = Decimal('0.015')  # Exit at 1.5% instead of 1%
```

### 2. Reduce max hold time
```python
MAX_POSITION_TIME = 120  # Force exit after 2 minutes
```

### 3. Manual intervention

Check active positions:
```python
# In Python shell on VPS
from polymarket_bot.bot import *
# Check self.executor.get_active_positions()
```

Or add a manual close function to bot.py:
```python
async def emergency_close_all(self):
    """Manually close all positions"""
    for pos_id, pos in list(self.executor.active_positions.items()):
        await self.executor.emergency_close_position(pos)
```

---

## Issue: Circuit breaker keeps activating

**Cause:** Too many losing trades triggering safety mechanism.

**Options:**

### 1. Adjust circuit breaker thresholds

Edit `polymarket_bot/risk_manager.py` around line 26:
```python
self.max_consecutive_losses = 10  # Up from 5
```

### 2. Manually reset
```python
# SSH into VPS
# In Python:
from polymarket_bot.bot import *
bot.risk_manager.deactivate_circuit_breaker()
```

### 3. THIS IS A WARNING SIGN
If the circuit breaker keeps firing, the strategy may not be profitable. Review your trades to understand why you're losing.

---

## Issue: Bot crashes with "Insufficient funds"

**Cause:** Not enough USDC to place orders.

**Solutions:**

### 1. Check wallet balance (see script above)

### 2. Reduce position size
```python
POSITION_SIZE = Decimal('20')  # Smaller positions
```

### 3. Bridge more USDC to Polygon

---

## Issue: High slippage eating profits

**Cause:** Low liquidity markets, or market orders hitting worse price levels.

**Solutions:**

### 1. Increase minimum liquidity requirement
```python
MIN_LIQUIDITY = Decimal('20000')  # Only trade deep markets
```

### 2. Reduce position size relative to market size
```python
# Only trade position sizes that are <1% of market liquidity
# Add this check in executor.py
if position_size > (market_data.liquidity * Decimal('0.01')):
    logger.warning("Position too large for market")
    return None
```

---

## Issue: Bot not detecting any arbitrage opportunities

**Cause:** Markets are efficient, or parameters too strict.

**Solutions:**

### 1. Relax spread threshold
```python
MIN_SPREAD = Decimal('0.01')  # Accept 1% spreads
```

### 2. Check if opportunities actually exist

Manually monitor a BTC market on Polymarket during news events. Do you see prices spike irrationally? If not, opportunities may be rare.

### 3. This might mean the strategy doesn't work

Be prepared for the possibility that:
- Markets are too efficient
- Other bots are faster
- The edge described in the tweet was exaggerated

---

## Issue: Errors about "py_clob_client" or imports

**Cause:** Dependencies not installed correctly.

**Fix:**
```bash
cd /root/testkaro
source venv/bin/activate
pip install --upgrade py-clob-client web3 eth-account
```

---

## Issue: "Connection refused" or "RPC errors"

**Cause:** RPC endpoint down or rate limited.

**Solutions:**

### 1. Use Alchemy or Infura (not free public RPC)

### 2. Add retry logic

The bot should already retry, but you can increase delays in `market_monitor.py`:
```python
await asyncio.sleep(5)  # Wait longer between requests
```

---

## Issue: Want to track performance better

**Solution: Add performance tracking**

Create `polymarket_bot/performance_tracker.py`:
```python
import json
from datetime import datetime
from decimal import Decimal

class PerformanceTracker:
    def __init__(self, filename='performance.json'):
        self.filename = filename
        self.trades = []

    def record_trade(self, trade_data):
        trade_data['timestamp'] = datetime.now().isoformat()
        self.trades.append(trade_data)
        self._save()

    def _save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.trades, f, indent=2, default=str)

    def get_stats(self):
        if not self.trades:
            return {}

        wins = [t for t in self.trades if t.get('pnl', 0) > 0]
        losses = [t for t in self.trades if t.get('pnl', 0) < 0]

        return {
            'total_trades': len(self.trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(self.trades) * 100,
            'total_pnl': sum(t.get('pnl', 0) for t in self.trades),
            'avg_win': sum(t['pnl'] for t in wins) / len(wins) if wins else 0,
            'avg_loss': sum(t['pnl'] for t in losses) / len(losses) if losses else 0
        }
```

Integrate into bot.py to track every closed position.

---

## Emergency: Need to stop bot and close all positions

```bash
# 1. Stop the bot
screen -r polymarket
# Press Ctrl+C

# Or if using systemd:
systemctl stop polymarket-bot

# 2. Check active positions
# The bot should have closed them on shutdown, but verify

# 3. Manual close if needed
# Go to https://polymarket.com/ and manually sell your positions

# 4. Withdraw funds from wallet
# Send USDC back to your safe wallet address
```

---

## General Debugging

**Enable debug logging:**
```bash
# Edit .env
LOG_LEVEL=DEBUG
```

**Watch logs in real-time:**
```bash
tail -f polymarket_bot.log
# Or
journalctl -u polymarket-bot -f
```

**Python debugging:**
```bash
cd /root/testkaro
source venv/bin/activate
python

>>> from polymarket_bot.bot import *
>>> import asyncio
>>> # Test components individually
```
