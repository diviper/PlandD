"""Base message handlers"""
import logging
import traceback
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from pland.core.config import Config
from pland.bot.keyboards import get_main_keyboard

logger = logging.getLogger(__name__)

async def start_command(message: Message):
    """Handle /start command"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        logger.info(f"=== Начало обработки команды /start ===")
        logger.info(f"От пользователя: {username} (ID: {user_id})")

        welcome_message = (
            "👋 Привет! Я помогу тебе организовать твои задачи и время.\n\n"
            "🤖 Я умею:\n"
            "• Анализировать задачи и создавать оптимальный план\n"
            "• Учитывать твой режим и уровень энергии\n"
            "• Напоминать о важных делах\n\n"
            "📝 Просто опиши свою задачу, и я помогу её организовать!\n"
            "Например: 'Нужно подготовить презентацию к завтрашней встрече'\n\n"
            "❓ Используй /help для получения списка всех команд"
        )

        try:
            await message.answer(
                welcome_message,
                reply_markup=get_main_keyboard()
            )
            logger.info(f"✓ Отправлено приветственное сообщение пользователю {username}")
        except Exception as send_error:
            logger.error(f"❌ Ошибка при отправке сообщения: {str(send_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    except Exception as e:
        logger.error(f"❌ Ошибка при обработке команды /start: {str(e)}")
        logger.error(f"Полный traceback: {traceback.format_exc()}")
        try:
            await message.answer(
                "Произошла ошибка при обработке команды. "
                "Пожалуйста, попробуйте позже."
            )
        except Exception as reply_error:
            logger.error(f"❌ Не удалось отправить сообщение об ошибке: {str(reply_error)}")

async def help_command(message: Message):
    """Handle /help command"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        logger.info(f"=== Начало обработки команды /help ===")
        logger.info(f"От пользователя: {username} (ID: {user_id})")

        commands_list = "\n".join([f"/{cmd} - {desc}" for cmd, desc in Config.COMMANDS.items()])
        help_message = (
            f"📚 Доступные команды:\n\n{commands_list}\n\n"
            "✍️ Создание задач:\n"
            "1. Отправьте текстовое сообщение с описанием задачи\n\n"
            "📱 Примеры задач:\n"
            "• 'Нужно подготовить презентацию к завтрашней встрече'\n"
            "• 'В пятницу важное собеседование, надо подготовиться'\n"
            "• 'Через неделю день рождения мамы, нужно организовать праздник'\n\n"
            "⚡️ Управление задачами:\n"
            "/list - Показать все задачи\n"
            "/upcoming - Показать ближайшие задачи\n"
            "/edit [ID] - Редактировать задачу\n"
            "/done [ID] - Отметить задачу выполненной\n"
            "/delete [ID] - Удалить задачу"
        )

        try:
            await message.answer(
                help_message,
                reply_markup=get_main_keyboard()
            )
            logger.info(f"✓ Отправлен список команд пользователю {username}")
        except Exception as send_error:
            logger.error(f"❌ Ошибка при отправке сообщения: {str(send_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    except Exception as e:
        logger.error(f"❌ Ошибка при обработке команды /help: {str(e)}")
        logger.error(f"Полный traceback: {traceback.format_exc()}")
        try:
            await message.answer(
                "Произошла ошибка при обработке команды. "
                "Пожалуйста, попробуйте позже."
            )
        except Exception as reply_error:
            logger.error(f"❌ Не удалось отправить сообщение об ошибке: {str(reply_error)}")

def register_base_handlers(router: Router):
    """Register base message handlers"""
    try:
        logger.info("=== Регистрация базовых обработчиков ===")

        # Регистрируем обработчик команды /start
        router.message.register(start_command, Command(commands=["start"]))
        logger.info("✓ Зарегистрирован обработчик команды /start")

        # Регистрируем обработчик команды /help
        router.message.register(help_command, Command(commands=["help"]))
        logger.info("✓ Зарегистрирован обработчик команды /help")

        logger.info("=== Регистрация базовых обработчиков завершена ===")

    except Exception as e:
        logger.error(f"❌ Ошибка при регистрации обработчиков: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise