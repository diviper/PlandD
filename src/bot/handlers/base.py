"""Base message handlers"""
import logging
import traceback
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.methods import SendMessage

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

async def start_command(message: Message) -> SendMessage:
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
        
        return SendMessage(chat_id=message.chat.id, text=text, reply_markup=get_main_keyboard())

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /start: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return SendMessage(chat_id=message.chat.id, text=error_msg)

async def help_command(message: Message) -> SendMessage:
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
        
        return SendMessage(chat_id=message.chat.id, text=text, reply_markup=get_main_keyboard())

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /help: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return SendMessage(chat_id=message.chat.id, text=error_msg)

async def settings_command(message: Message) -> SendMessage:
    """Обработка команды /settings"""
    try:
        settings_text = (
            "⚙️ <b>Настройки:</b>\n\n"
            "🕒 Предпочтительное время для задач\n"
            "📊 Уровень детализации планов\n"
            "🔔 Настройки уведомлений\n\n"
            "🚧 Эта функция находится в разработке...\n\n"
            "<i>Скоро вы сможете настроить:</i>\n"
            "• Часы повышенной продуктивности\n"
            "• Предпочтительную длительность задач\n"
            "• Частоту напоминаний"
        )

        return SendMessage(chat_id=message.chat.id, text=settings_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /settings: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return SendMessage(chat_id=message.chat.id, text=error_msg)

async def stats_command(message: Message) -> SendMessage:
    """Обработка команды /stats"""
    try:
        stats_text = (
            "📊 <b>Статистика и прогресс</b>\n\n"
            "🚧 Эта функция находится в разработке...\n\n"
            "<i>Скоро здесь появится:</i>\n"
            "• Количество выполненных задач\n"
            "• Статистика по типам задач\n"
            "• Анализ продуктивности\n"
            "• Рекомендации по улучшению"
        )

        return SendMessage(chat_id=message.chat.id, text=stats_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /stats: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return SendMessage(chat_id=message.chat.id, text=error_msg)

async def handle_text_message(message: Message) -> SendMessage:
    """
    Handle text messages
    """
    try:
        if message.text == "📝 новый план":
            text = (
                "Отлично! Давай создадим новый план! *burp* 🥒\n\n"
                "Просто напиши мне свой план, и я помогу тебе его оптимизировать!"
            )
            return SendMessage(chat_id=message.chat.id, text=text, reply_markup=get_main_keyboard())
        elif message.text == "❓ помощь":
            return await help_command(message)
        elif message.text == "⚙️ настройки":
            return await settings_command(message)
        elif message.text == "📊 прогресс":
            return await stats_command(message)
        else:
            text = (
                "Я не понимаю, что ты хочешь, Морти! *burp* 🥒\n\n"
                "Используй команды:\n"
                "• /plan - создать новый план\n"
                "• /help - получить помощь"
            )
            return SendMessage(chat_id=message.chat.id, text=text, reply_markup=get_main_keyboard())

    except Exception as e:
        error_msg = f"Ошибка при обработке текстового сообщения: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return SendMessage(chat_id=message.chat.id, text=error_msg)

def register_base_handlers(dp: Router):
    """Регистрация базовых обработчиков"""
    # Команды
    router.message.register(start_command, Command("start"))
    router.message.register(help_command, Command("help"))
    router.message.register(settings_command, Command("settings"))
    router.message.register(stats_command, Command("stats"))
    
    # Текстовые сообщения
    router.message.register(handle_text_message, F.text)
    
    # Подключаем роутер к диспетчеру, если он еще не подключен
    if router.parent_router is None:
        dp.include_router(router)