"""Base message handlers"""
import logging
import traceback
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from src.core.config import Config
from src.bot.keyboards import get_main_keyboard

logger = logging.getLogger(__name__)

async def start_command(message: Message):
    """Handle /start command"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        logger.info(f"=== Начало обработки команды /start ===")
        logger.info(f"От пользователя: {username} (ID: {user_id})")

        welcome_message = (
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            "Я твой персональный помощник в планировании задач. "
            "Я использую искусственный интеллект, чтобы помочь тебе:\n\n"
            "✅ Анализировать задачи\n"
            "📋 Разбивать их на подзадачи\n"
            "⏰ Устанавливать оптимальные сроки\n"
            "🔔 Напоминать о важных делах\n\n"
            "Просто напиши мне свою задачу, и я помогу её организовать!"
        )

        await message.answer(
            welcome_message,
            reply_markup=get_main_keyboard()
        )
        logger.info("✓ Команда /start обработана успешно")

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /start: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        await message.answer(
            "🚫 Произошла ошибка при обработке команды.\n"
            "Пожалуйста, попробуйте позже."
        )

async def help_command(message: Message):
    """Handle /help command"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        logger.info(f"=== Начало обработки команды /help ===")
        logger.info(f"От пользователя: {username} (ID: {user_id})")

        help_message = (
            "🤖 <b>Как пользоваться ботом:</b>\n\n"
            "1️⃣ <b>Добавление задачи:</b>\n"
            "   • Просто напишите вашу задачу\n"
            "   • Я проанализирую её и помогу организовать\n\n"
            "2️⃣ <b>Основные команды:</b>\n"
            "   /start - Начать работу\n"
            "   /help - Показать эту справку\n"
            "   /tasks - Список ваших задач\n"
            "   /settings - Настройки\n\n"
            "3️⃣ <b>Управление задачами:</b>\n"
            "   • Отмечайте выполненные задачи\n"
            "   • Получайте напоминания\n"
            "   • Следите за прогрессом\n\n"
            "4️⃣ <b>Дополнительно:</b>\n"
            "   • Минимальная длина задачи: {min_len} символов\n"
            "   • Максимальная длина: {max_len} символов\n"
            "   • Напоминания: за {reminder} минут до дедлайна\n"
        ).format(
            min_len=Config.MIN_TASK_LENGTH,
            max_len=Config.MAX_TASK_LENGTH,
            reminder=Config.DEFAULT_REMINDER_MINUTES
        )

        await message.answer(
            help_message,
            reply_markup=get_main_keyboard()
        )
        logger.info("✓ Команда /help обработана успешно")

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /help: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        await message.answer(
            "🚫 Произошла ошибка при обработке команды.\n"
            "Пожалуйста, попробуйте позже."
        )

def register_base_handlers(router: Router):
    """Register base message handlers"""
    try:
        # Регистрируем обработчик команды /start
        router.message.register(
            start_command,
            Command(commands=["start"])
        )
        logger.debug("✓ Зарегистрирован обработчик команды /start")

        # Регистрируем обработчик команды /help
        router.message.register(
            help_command,
            Command(commands=["help"])
        )
        logger.debug("✓ Зарегистрирован обработчик команды /help")

    except Exception as e:
        logger.error(f"Ошибка при регистрации базовых обработчиков: {str(e)}")
        raise