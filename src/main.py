import asyncio
import logging
from pland.bot import start_bot

def main():
    """
    Точка входа для запуска Telegram бота PlanD
    """
    logging.basicConfig(level=logging.INFO)
    
    try:
        asyncio.run(start_bot())
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main()