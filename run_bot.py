#!/usr/bin/env python3
"""
Convenience script to run the Polymarket bot
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the polymarket_bot directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Run the bot
if __name__ == "__main__":
    from polymarket_bot.bot import main
    import asyncio

    asyncio.run(main())
