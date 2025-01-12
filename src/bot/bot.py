"""Basic Telegram bot implementation"""
import logging
import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ErrorEvent

from src.bot.handlers import register_handlers
from src.bot.handlers.plan_handler import register_handlers as register_plan_handlers
from src.core.config import Config
from src.database.database import Database
from src.database.db import init_db
from src.services.reminder import ReminderScheduler, Notifier

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
            await message.answer(
                "🚫 Произошла ошибка при обработке сообщения.\n"
                "Пожалуйста, попробуйте позже."
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения об ошибке: {str(e)}")
    return True

async def run_bot():
    """Run the bot with all handlers and services"""
    try:
        # Проверяем наличие необходимых токенов
        if not Config.BOT_TOKEN or not Config.OPENAI_API_KEY:
            logger.error("Отсутствуют необходимые токены")
            return

        # Инициализируем базу данных
        logger.info("Инициализация базы данных...")
        init_db()
        db = Database()

        # Инициализируем бота
        logger.info("Инициализация бота...")
        bot = Bot(
            token=Config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML")
        )

        if not await check_bot_token(bot):
            return

        try:
            # Настраиваем диспетчер и хранилище
            logger.info("Настройка диспетчера и хранилища...")
            storage = MemoryStorage()
            dp = Dispatcher(storage=storage)

            # Создаем основной роутер
            main_router = Router(name="main_router")
            dp.include_router(main_router)

            # Инициализируем сервисы напоминаний
            logger.info("Инициализация сервисов напоминаний...")
            notifier = Notifier(bot)
            scheduler = ReminderScheduler(bot, db)
            scheduler.start()

            # Регистрируем обработчики
            logger.info("Регистрация обработчиков...")
            def setup_handlers(dp: Dispatcher):
                """Setup message handlers"""
                # Register base handlers
                register_handlers(dp, db)
                
                # Register plan handlers
                register_plan_handlers(dp)
                
            setup_handlers(dp)

            # Регистрируем глобальный обработчик ошибок
            dp.errors.register(error_handler)

            logger.info("Запуск бота в режиме long polling...")
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
            scheduler.stop()

    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(run_bot())