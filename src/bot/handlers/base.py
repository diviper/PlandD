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
        logger.error(f"Ошибка при обработке команды /start: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(
            "😓 Произошла ошибка при обработке команды.\n"
            "Пожалуйста, попробуйте позже."
        )

async def help_command(message: Message):
    """Обработка команды /help"""
    try:
        help_text = (
            "🔍 <b>Доступные команды:</b>\n\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/settings - Настройки планирования\n"
            "/stats - Статистика и прогресс\n\n"
            "<b>Как пользоваться:</b>\n"
            "1. Просто напиши свою задачу или план\n"
            "2. Я проанализирую и помогу организовать\n"
            "3. Используй кнопки для быстрого доступа\n\n"
            "<b>Советы:</b>\n"
            "• Описывай задачи подробно\n"
            "• Указывай сроки и приоритеты\n"
            "• Используй метод Помодоро для эффективной работы\n"
            "• Регулярно проверяй прогресс через /stats"
        )

        await message.answer(
            help_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        logger.info(f"Команда /help обработана для пользователя {message.from_user.id}")

    except Exception as e:
        logger.error(f"Ошибка при обработке команды /help: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(
            "😓 Произошла ошибка при обработке команды.\n"
            "Пожалуйста, попробуйте позже."
        )

async def settings_command(message: Message):
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

        await message.answer(
            settings_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        logger.info(f"Команда /settings обработана для пользователя {message.from_user.id}")

    except Exception as e:
        logger.error(f"Ошибка при обработке команды /settings: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(
            "😓 Произошла ошибка при обработке команды.\n"
            "Пожалуйста, попробуйте позже."
        )

async def stats_command(message: Message):
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

        await message.answer(
            stats_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        logger.info(f"Команда /stats обработана для пользователя {message.from_user.id}")

    except Exception as e:
        logger.error(f"Ошибка при обработке команды /stats: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(
            "😓 Произошла ошибка при обработке команды.\n"
            "Пожалуйста, попробуйте позже."
        )

async def handle_text_message(message: Message):
    """Обработка текстовых сообщений"""
    try:
        text = message.text.lower()
        
        if text == "📝 новый план":
            # Перенаправляем на команду /plan
            await message.answer(
                "Воу-воу, *burp* какие планы на сегодня?\n"
                "Давай, Морти, выкладывай свои дела, а я *burp* разложу их по полочкам!\n"
                "Только без этой занудной ерунды, ок?",
                parse_mode="Markdown"
            )
        elif text == "❓ помощь":
            await help_command(message)
        elif text == "⚙️ настройки":
            await settings_command(message)
        elif text == "📊 прогресс":
            await stats_command(message)
        else:
            await message.answer(
                "Эй, Морти, я не совсем *burp* понял, что ты хочешь.\n"
                "Используй кнопки или команды, чтобы я мог тебе помочь!",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при обработке текстового сообщения: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(
            "😓 Произошла ошибка при обработке сообщения.\n"
            "Пожалуйста, попробуйте позже."
        )

def register_base_handlers(dp: Router):
    """Регистрация базовых обработчиков"""
    # Команды
    router.message.register(start_command, Command("start"))
    router.message.register(help_command, Command("help"))
    router.message.register(settings_command, Command("settings"))
    router.message.register(stats_command, Command("stats"))
    
    # Текстовые сообщения
    router.message.register(handle_text_message, F.text)
    
    # Подключаем роутер к диспетчеру
    dp.include_router(router)