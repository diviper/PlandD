"""Basic Telegram bot implementation"""
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ErrorEvent

from pland.bot.handlers import register_handlers
from pland.core.config import Config
from pland.database.database import Database

logger = logging.getLogger(__name__)

async def check_bot_token(bot: Bot) -> bool:
    """Проверяет валидность токена бота"""
    try:
        bot_info = await bot.get_me()
        logger.info(f"Бот успешно подключен: @{bot_info.username}")
        return True
    except TelegramAPIError as e:
        logger.error(f"Ошибка Telegram API при проверке токена: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {str(e)}", exc_info=True)
        return False

async def error_handler(event: ErrorEvent, data: dict) -> bool:
    """Глобальный обработчик ошибок"""
    logger.error("Произошла ошибка при обработке события", exc_info=event.exception)
    try:
        message = data.get("event_update", {}).get("message")
        if message and isinstance(message, Message):
            await message.answer("Произошла ошибка при обработке сообщения")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения об ошибке: {str(e)}")
    return True

async def run_bot():
    """Run the bot with all handlers and services"""
    try:
        if not Config.BOT_TOKEN or not Config.OPENAI_API_KEY:
            logger.error("Отсутствуют необходимые токены")
            return

        bot = Bot(
            token=Config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML")
        )

        if not await check_bot_token(bot):
            return

        try:
            storage = MemoryStorage()
            dp = Dispatcher(storage=storage)
            db = Database()

            router = Router(name="main_router")
            register_handlers(router, db)
            dp.include_router(router)
            dp.errors.register(error_handler)

            logger.info("Starting long polling")
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types(),
                skip_updates=True
            )

        except Exception as e:
            logger.error(f"Ошибка при работе бота: {str(e)}", exc_info=True)
            raise
        finally:
            await bot.session.close()

    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())