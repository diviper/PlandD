"""Base message handlers"""
import logging
import traceback
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from src.core.config import Config

logger = logging.getLogger(__name__)

# Создаем роутер для базовых обработчиков
router = Router(name="base")

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

async def start_command(message: Message) -> None:
    """
    Handle /start command
    """
    try:
        logger.info("=== Начало обработки команды /start ===")
        logger.info(f"От пользователя: {message.from_user.username} (ID: {message.from_user.id})")

        text = (
            "Привет, мешок с костями! 🦴\n\n"
            "Я твой персональный планировщик задач в стиле Рика из 'Рик и Морти'! *burp* 🥒\n\n"
            "Вот что я могу:\n"
            "• /plan - создать новый план\n"
            "• /help - получить помощь\n\n"
            "Давай начнем планировать что-нибудь безумное! 🚀"
        )
        
        await message.answer(text=text, reply_markup=get_main_keyboard())

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /start: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(text=error_msg)

async def help_command(message: Message) -> None:
    """
    Handle /help command
    """
    try:
        text = (
            "О, ты нуждаешься в моей помощи? *burp* 🥒\n\n"
            "Вот список команд:\n"
            "• /plan - создать новый план\n"
            "• /help - показать это сообщение\n\n"
            "Просто выбери команду, и погнали! 🚀"
        )
        
        await message.answer(text=text, reply_markup=get_main_keyboard())

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /help: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(text=error_msg)

async def settings_command(message: Message) -> None:
    """
    Handle /settings command
    """
    try:
        text = (
            "⚙️ Настройки:\n\n"
            "• Частота напоминаний\n"
            "• Формат отображения планов\n"
            "• Уведомления\n"
            "• Часовой пояс\n\n"
            "(Функционал в разработке)"
        )
        
        await message.answer(text=text, reply_markup=get_main_keyboard())

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /settings: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(text=error_msg)

async def stats_command(message: Message) -> None:
    """
    Handle /stats command
    """
    try:
        text = (
            "📊 Статистика:\n\n"
            "• Выполненные планы\n"
            "• Текущие планы\n"
            "• Эффективность\n"
            "• Рекомендации\n\n"
            "(Функционал в разработке)"
        )
        
        await message.answer(text=text, reply_markup=get_main_keyboard())

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /stats: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(text=error_msg)

async def handle_text_message(message: Message):
    """
    Handle text messages
    """
    try:
        if message.text == "📝 Новый план":
            text = (
                "Отлично! Давай создадим новый план! *burp* 🥒\n\n"
                "Просто напиши мне свой план, и я помогу тебе его оптимизировать!"
            )
            await message.answer(text=text, reply_markup=get_main_keyboard())
        elif message.text == "❓ Помощь":
            await message.answer(
                text=(
                    "О, ты нуждаешься в моей помощи? *burp* 🥒\n\n"
                    "Вот список команд:\n"
                    "• /plan - создать новый план\n"
                    "• /help - показать это сообщение\n\n"
                    "Просто выбери команду, и погнали! 🚀"
                ),
                reply_markup=get_main_keyboard()
            )
        elif message.text == "⚙️ Настройки":
            await message.answer(
                text=(
                    "⚙️ Настройки:\n\n"
                    "• Частота напоминаний\n"
                    "• Формат отображения планов\n"
                    "• Уведомления\n"
                    "• Часовой пояс\n\n"
                    "(Функционал в разработке)"
                ),
                reply_markup=get_main_keyboard()
            )
        elif message.text == "📊 Прогресс":
            await message.answer(
                text=(
                    "📊 Статистика:\n\n"
                    "• Выполненные планы\n"
                    "• Текущие планы\n"
                    "• Эффективность\n"
                    "• Рекомендации\n\n"
                    "(Функционал в разработке)"
                ),
                reply_markup=get_main_keyboard()
            )
        else:
            text = (
                "Я не понимаю, что ты хочешь, Морти! *burp* 🥒\n\n"
                "Используй команды:\n"
                "• /plan - создать новый план\n"
                "• /help - получить помощь"
            )
            await message.answer(text=text, reply_markup=get_main_keyboard())

    except Exception as e:
        error_msg = f"Ошибка при обработке текстового сообщения: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(text=error_msg)

def register_base_handlers(dp: Router):
    """Регистрация базовых обработчиков"""
    # Создаем роутер для базовых обработчиков
    base_router = Router(name="base_router")
    
    # Команды
    base_router.message.register(start_command, Command("start"))
    base_router.message.register(help_command, Command("help"))
    base_router.message.register(settings_command, Command("settings"))
    base_router.message.register(stats_command, Command("stats"))
    
    # Текстовые сообщения для кнопок меню
    base_router.message.register(
        handle_text_message,
        F.text.in_({
            "📝 Новый план",
            "📋 Мои планы",
            "📊 Прогресс",
            "⚙️ Настройки",
            "❓ Помощь"
        })
    )
    
    # Подключаем роутер к основному роутеру
    dp.include_router(base_router)