"""Main entry point for the Telegram bot"""
import asyncio
import logging
import sys
import os

from pland.bot.bot import run_bot
from pland.core.config import setup_logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Добавляем отладочную информацию о переменных окружения
        logger.info("=== Starting PlanD Bot ===")
        logger.info(f"OpenAI API Key present: {'*' * 5}{os.getenv('OPENAI_API_KEY', '')[-4:]}")
        logger.info(f"Bot Token present: {'*' * 5}{os.getenv('BOT_TOKEN', '')[-4:]}")

        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
        sys.exit(1)