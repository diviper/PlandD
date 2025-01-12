"""Base message handlers"""
import logging
import traceback
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from src.core.config import Config

logger = logging.getLogger(__name__)

def get_main_keyboard():
    """Создает основную клавиатуру"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Новый план")],
            [KeyboardButton(text="📋 Мои планы"), KeyboardButton(text="📊 Прогресс")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return keyboard

async def start_command(message: Message):
    """Обработка команды /start"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        logger.info(f"=== Начало обработки команды /start ===")
        logger.info(f"От пользователя: {username} (ID: {user_id})")

        welcome_message = (
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            "Я твой AI-помощник в планировании. Я помогу тебе:\n\n"
            "📝 Создавать эффективные планы\n"
            "🎯 Достигать поставленных целей\n"
            "⏰ Управлять временем\n"
            "📊 Отслеживать прогресс\n\n"
            "Чтобы начать:\n"
            "1. Нажми '📝 Новый план' или используй /plan\n"
            "2. Опиши свою цель или задачу\n"
            "3. Я помогу разбить её на конкретные шаги\n\n"
            "Используй /help для списка всех команд!"
        )

        await message.answer(
            welcome_message,
            reply_markup=get_main_keyboard()
        )
        logger.info("✓ Команда /start обработана успешно")

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /start: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        await message.answer(
            "😔 Извините, произошла ошибка при запуске бота.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )

async def help_command(message: Message):
    """Обработка команды /help"""
    try:
        help_text = (
            "🤖 <b>Доступные команды:</b>\n\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/plan - Создать новый план\n"
            "/plans - Показать все планы\n"
            "/progress - Статистика выполнения\n"
            "/settings - Настройки бота\n\n"
            "🔍 <b>Как пользоваться:</b>\n"
            "1. Создайте новый план через /plan\n"
            "2. Опишите свою цель\n"
            "3. Следуйте моим рекомендациям\n\n"
            "💡 <b>Советы:</b>\n"
            "• Описывайте цели конкретно\n"
            "• Указывайте сроки выполнения\n"
            "• Регулярно отмечайте прогресс"
        )

        await message.answer(
            help_text,
            parse_mode="HTML"
        )
        logger.info(f"✓ Команда /help выполнена для пользователя {message.from_user.id}")

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /help: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        await message.answer("😔 Не удалось показать справку. Попробуйте позже.")

async def settings_command(message: Message):
    """Обработка команды /settings"""
    try:
        settings_text = (
            "⚙️ <b>Настройки:</b>\n\n"
            "🔔 Уведомления: Включены\n"
            "🕐 Часовой пояс: UTC+3\n"
            "🌍 Язык: Русский\n\n"
            "<i>Скоро здесь появятся дополнительные настройки!</i>"
        )

        await message.answer(
            settings_text,
            parse_mode="HTML"
        )
        logger.info(f"✓ Команда /settings выполнена для пользователя {message.from_user.id}")

    except Exception as e:
        logger.error(f"Ошибка в settings_command: {e}\n{traceback.format_exc()}")
        await message.answer("😔 Не удалось открыть настройки. Попробуйте позже.")

def register_base_handlers(router: Router):
    """Регистрация базовых обработчиков сообщений"""
    router.message.register(start_command, Command("start"))
    router.message.register(help_command, Command("help"))
    router.message.register(settings_command, Command("settings"))
    
    logger.info("✓ Базовые обработчики сообщений зарегистрированы")