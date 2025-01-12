"""Main entry point for the Telegram bot"""
import asyncio
import logging
import sys

from pland.bot.bot import run_bot
from pland.core.config import setup_logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        setup_logging()
        logger.info("=== Starting PlanD Bot ===")
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error: {str(e)}", exc_info=True)
        sys.exit(1)