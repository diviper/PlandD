"""Basic Telegram bot implementation"""
import logging
import sys
import os
from typing import Any, Dict

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ErrorEvent

from pland.bot.handlers import register_handlers
from pland.core.config import Config
from pland.database.database import Database
from pland.services.reminder import ReminderScheduler

logger = logging.getLogger(__name__)

async def check_bot_token(bot: Bot) -> bool:
    """Проверяет валидность токена бота"""
    try:
        logger.debug("Начало проверки токена бота")
        logger.debug(f"Используется токен: ...{Config.BOT_TOKEN[-4:]}")
        bot_info = await bot.get_me()
        logger.info(f"Бот успешно подключен: @{bot_info.username}")
        # Добавляем дополнительную информацию о боте
        logger.info(f"ID бота: {bot_info.id}")
        logger.info(f"Имя бота: {bot_info.first_name}")
        logger.info(f"Может присоединяться к группам: {bot_info.can_join_groups}")
        logger.info(f"Может читать сообщения групп: {bot_info.can_read_all_group_messages}")
        return True
    except TelegramAPIError as e:
        logger.error(f"Ошибка Telegram API при проверке токена: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при проверке токена бота: {str(e)}", exc_info=True)
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
        logger.debug("Проверка переменных окружения...")

        # Проверка наличия токенов с детальным логированием
        if not Config.BOT_TOKEN:
            logger.error("Токен бота не найден в переменных окружения!")
            logger.debug("Проверьте наличие переменной BOT_TOKEN в файле .env")
            return

        if not Config.OPENAI_API_KEY:
            logger.error("Ключ OpenAI API не найден в переменных окружения!")
            logger.debug("Проверьте наличие переменной OPENAI_API_KEY в файле .env")
            return

        logger.debug(f"Токен бота найден: ...{Config.BOT_TOKEN[-4:]}")
        logger.debug(f"OpenAI API ключ найден: ...{Config.OPENAI_API_KEY[-4:]}")

        # Инициализация бота с подробным логированием
        logger.debug("Инициализация бота...")
        bot = Bot(
            token=Config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML")
        )

        # Проверка подключения к Telegram API
        logger.debug("Проверка подключения к Telegram API...")
        if not await check_bot_token(bot):
            logger.error("Не удалось подключиться к Telegram API. Проверьте токен бота.")
            return

        # Инициализация компонентов
        logger.debug("Инициализация компонентов...")
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        logger.debug(f"Диспетчер создан с хранилищем: {type(storage).__name__}")

        logger.debug(f"Инициализация базы данных")
        db = Database()

        # Добавляем отладочные сообщения для отслеживания регистрации обработчиков
        logger.debug("Начало регистрации обработчиков...")

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

        # Запуск поллинга с подробным логированием
        logger.info("=== Запуск поллинга ===")
        logger.debug("Настройка параметров поллинга...")

        try:
            logger.debug("Запуск поллинга с параметрами:")
            logger.debug(f"- Разрешенные обновления: {dp.resolve_used_update_types()}")
            logger.debug(f"- Пропуск накопленных сообщений: True")

            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types(),
                skip_updates=True
            )
            logger.info("✓ Поллинг успешно запущен")
        except TelegramAPIError as e:
            logger.error(f"Ошибка Telegram API при запуске поллинга: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при запуске поллинга: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())