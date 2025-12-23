# Polymarket Arbitrage Bot

A Python trading bot that exploits mean reversion and price inefficiencies on Polymarket's BTC 15-minute markets.

## Strategy Overview

The bot implements a gap-trading arbitrage strategy:

1. **Monitors** BTC 15-minute markets on Polymarket in real-time
2. **Detects** price gaps when one side (YES/NO) moves faster due to emotional trading
3. **Enters** both sides simultaneously when spreads widen beyond threshold
4. **Exits** when the spread normalizes back, capturing the mean reversion

**Target profit:** $15-$70 per trade, compounded repeatedly

## How It Works

When news hits, markets overreact. Prices jump hard for a few seconds (sometimes minutes), not because probabilities actually changed, but because people rush in emotionally.

In an efficient binary market: `YES price + NO price ≈ 1.0`

When this relationship breaks down, the bot:
- Buys both YES and NO sides at inflated prices
- Waits for emotional traders to exit
- Sells both sides when prices normalize
- Captures the spread as profit

## Features

- **Real-time market monitoring** via Polymarket's CLOB API
- **Gap detection** algorithm to identify one-sided price movements
- **Risk management** with exposure limits, stop losses, and circuit breakers
- **Position management** with automatic exits
- **Paper trading mode** (DRY_RUN) for safe testing
- **Comprehensive logging** of all trades and decisions

## Project Structure

```
polymarket_bot/
├── __init__.py          # Package initialization
├── config.py            # Configuration and parameters
├── polymarket_client.py # Polymarket API wrapper
├── market_monitor.py    # Market data monitoring
├── strategy.py          # Arbitrage strategy logic
├── executor.py          # Order execution
├── position_manager.py  # Position management
├── risk_manager.py      # Risk controls
└── bot.py              # Main bot runner

run_bot.py              # Convenience script to run the bot
requirements.txt        # Python dependencies
.env.example           # Environment variables template
```

## Prerequisites

1. **Python 3.8+**
2. **Ethereum wallet** with USDC on Polygon network
3. **Private key** for your wallet (KEEP SECRET!)
4. **Basic understanding** of Polymarket and prediction markets

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd testkaro
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
nano .env  # Edit with your values
```

Required environment variables:

```bash
PRIVATE_KEY=your_ethereum_private_key_here
RPC_ENDPOINT=https://polygon-rpc.com
DRY_RUN=true  # Set to false for real trading
LOG_LEVEL=INFO
```

## Configuration

Edit `polymarket_bot/config.py` to adjust trading parameters:

### Trading Parameters

```python
MAX_EXPOSURE = 25000        # Maximum total exposure in USD
MIN_LIQUIDITY = 10000       # Minimum market liquidity required
POSITION_SIZE = 120         # Base position size per trade
```

### Strategy Parameters

```python
MIN_SPREAD = 0.02          # Minimum spread to trigger (2%)
TARGET_SPREAD = 0.05       # Ideal spread for entry (5%)
EXIT_SPREAD = 0.01         # Exit when spread narrows to 1%
```

### Risk Management

```python
MAX_POSITION_TIME = 300    # Max hold time (5 minutes)
STOP_LOSS_PERCENT = 0.03   # Stop loss at 3%
MIN_PROFIT_TARGET = 15     # Minimum profit per trade
MAX_PROFIT_TARGET = 70     # Maximum profit per trade
```

## Usage

### Running in Paper Trading Mode (Recommended First)

```bash
python run_bot.py
```

The bot will:
1. Connect to Polymarket
2. Discover BTC 15-minute markets
3. Monitor prices in real-time
4. Simulate trades (no real money)
5. Log all decisions

### Running in Live Trading Mode

**⚠️ WARNING: USE AT YOUR OWN RISK! ⚠️**

1. Ensure your wallet has USDC on Polygon
2. Set `DRY_RUN=false` in `.env`
3. Start small with low `POSITION_SIZE`
4. Monitor carefully

```bash
python run_bot.py
```

### Monitoring

The bot logs to both console and `polymarket_bot.log`:

```
[2025-12-23 10:15:23] INFO Discovering BTC 15m markets...
[2025-12-23 10:15:24] INFO Found 3 relevant BTC 15m markets
[2025-12-23 10:15:25] INFO Starting market monitoring loop...
[2025-12-23 10:15:30] INFO Arbitrage opportunity: spread=0.04, gap detected
[2025-12-23 10:15:31] INFO Position opened: abc123
[2025-12-23 10:16:15] INFO Spread normalized - take profit
[2025-12-23 10:16:16] INFO Position closed: abc123
[2025-12-23 10:16:16] INFO P&L: $38.40
```

## Risk Warnings

### Financial Risks

- **Loss of capital:** You can lose money trading
- **Slippage:** Actual execution prices may differ
- **Liquidity risk:** Low liquidity can prevent exits
- **Smart contract risk:** Polymarket contract vulnerabilities
- **Gas fees:** Transaction costs on Polygon

### Safety Features

The bot includes multiple safety mechanisms:

1. **Circuit breaker:** Stops trading after consecutive losses
2. **Daily loss limit:** Halts at 20% of max exposure loss
3. **Position timeouts:** Force closes positions held too long
4. **Liquidity checks:** Only trades sufficiently liquid markets
5. **Exposure limits:** Prevents over-leveraging

### Best Practices

1. **Start with paper trading** (DRY_RUN=true)
2. **Test extensively** before using real money
3. **Start small** with low position sizes
4. **Monitor actively** during first sessions
5. **Keep private keys secure** (never commit to git!)
6. **Backup your wallet** regularly
7. **Understand the strategy** before running

## Troubleshooting

### "No markets found"

- Check your internet connection
- Verify Polymarket API is accessible
- Adjust `BTC_MARKET_KEYWORDS` in config

### "Insufficient liquidity"

- Reduce `MIN_LIQUIDITY` threshold
- Wait for higher-volume markets
- Check market activity on Polymarket website

### "Max exposure reached"

- Close existing positions
- Increase `MAX_EXPOSURE` (carefully!)
- Wait for positions to exit

### "Circuit breaker active"

- Bot has hit safety limits
- Review logs for cause
- Manually deactivate if appropriate
- Adjust risk parameters

## Performance Tracking

The bot tracks:
- Total trades executed
- Win rate percentage
- Total P&L (profit/loss)
- Average hold time
- Daily P&L

View stats in the logs every 60 seconds.

## Disclaimer

**THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.**

- This bot is for educational purposes
- Trading involves significant risk
- Past performance ≠ future results
- You are responsible for your trades
- The authors are not liable for losses
- Use at your own risk

## Advanced Configuration

### Adjusting for Different Markets

To trade other markets, modify `config.py`:

```python
BTC_MARKET_KEYWORDS = ['your', 'market', 'keywords']
```

### Custom Strategy Parameters

Fine-tune the strategy by adjusting:
- Spread thresholds
- Position sizing
- Time limits
- Volatility filters

### Multiple Market Support

The bot can monitor multiple markets simultaneously. It will:
- Scan all matching markets
- Execute on best opportunities
- Manage positions independently

## Support & Contributing

For issues or questions:
1. Check the logs first
2. Review configuration
3. Test in paper trading mode
4. Open an issue with detailed logs

## License

MIT License - See LICENSE file

---

**Happy Trading! But remember: Only risk what you can afford to lose.**
