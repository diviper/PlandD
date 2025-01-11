"""Basic Telegram bot implementation"""
import logging
import sys
from typing import Any, Dict, Union

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ErrorEvent

from pland.bot.handlers import register_handlers
from pland.core.config import Config
from pland.database.database import Database
from pland.services.reminder import ReminderScheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

async def check_bot_token(bot: Bot) -> bool:
    """Проверяет валидность токена бота"""
    try:
        logger.debug("Начало проверки токена бота")
        bot_info = await bot.get_me()
        logger.info(f"Бот успешно подключен: @{bot_info.username}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при проверке токена бота: {str(e)}", exc_info=True)
        return False

async def error_handler(event: ErrorEvent, data: Dict[str, Any]) -> bool:
    """Глобальный обработчик ошибок"""
    logger.error("Произошла ошибка при обработке события", exc_info=event.exception)

    try:
        # Get the original message if available
        message = data.get("event_update", {}).get("message")
        if message and isinstance(message, Message):
            await message.answer(
                "Произошла ошибка при обработке сообщения. "
                "Пожалуйста, попробуйте позже."
            )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение об ошибке: {str(e)}", exc_info=True)

    # Return True to prevent error propagation
    return True

async def run_bot():
    """Run the bot with all handlers and services"""
    try:
        logger.info("=== Запуск бота ===")

        # Проверка наличия токенов
        if not Config.BOT_TOKEN:
            logger.error("Токен бота не найден в переменных окружения!")
            return

        if not Config.OPENAI_API_KEY:
            logger.error("Ключ OpenAI API не найден в переменных окружения!")
            return

        logger.info(f"OpenAI API Key доступен: {'*' * 5}{Config.OPENAI_API_KEY[-4:]}")

        # Инициализация бота
        bot = Bot(
            token=Config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML")
        )

        # Проверка подключения к Telegram API
        if not await check_bot_token(bot):
            logger.error("Не удалось подключиться к Telegram API. Проверьте токен бота.")
            return

        # Инициализация компонентов
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        db = Database(Config.DATABASE_PATH)

        # Регистрация глобального обработчика ошибок
        dp.errors.register(error_handler)
        logger.info("✓ Обработчик ошибок зарегистрирован")

        # Регистрируем обработчики
        router = Router(name="main_router")
        register_handlers(router, db)
        dp.include_router(router)
        logger.info("✓ Обработчики сообщений зарегистрированы")

        # Инициализация планировщика
        scheduler = ReminderScheduler(bot, db)
        scheduler.start()
        logger.info("✓ Планировщик напоминаний запущен")

        # Запуск поллинга
        logger.info("=== Запуск поллинга ===")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())