"""Test Telegram bot connection"""
import asyncio
import logging
from aiogram import Bot
from src.core.config import Config, setup_logging

async def test_bot():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    if not Config.BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не найден в .env файле")
        return
        
    try:
        print(f"🔄 Проверяем подключение к боту...")
        bot = Bot(token=Config.BOT_TOKEN)
        
        bot_info = await bot.get_me()
        print(f"✅ Бот успешно подключен!")
        print(f"Информация о боте:")
        print(f"- Username: @{bot_info.username}")
        print(f"- Имя: {bot_info.first_name}")
        print(f"- ID: {bot_info.id}")
        
    except Exception as e:
        print(f"❌ Ошибка при подключении к боту: {str(e)}")
    finally:
        if 'bot' in locals():
            await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(test_bot())
    except KeyboardInterrupt:
        print("\n⚠️ Тест остановлен пользователем")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
