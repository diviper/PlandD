"""Telegram bot keyboard layouts"""
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Create main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Добавить задачу")],
            [KeyboardButton(text="📋 Список задач")],
            [KeyboardButton(text="⏰ Настройки времени"), KeyboardButton(text="🍽 Приемы пищи")],
            [KeyboardButton(text="📊 Анализ дня"), KeyboardButton(text="⚖️ Баланс жизни")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_priority_keyboard() -> InlineKeyboardMarkup:
    """Create priority selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔴 Высокий", callback_data="priority_high"),
            InlineKeyboardButton(text="🟡 Средний", callback_data="priority_medium"),
            InlineKeyboardButton(text="🟢 Низкий", callback_data="priority_low")
        ]
    ])
    return keyboard

def get_meal_keyboard() -> InlineKeyboardMarkup:
    """Create meal type selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍳 Завтрак", callback_data="meal_breakfast"),
            InlineKeyboardButton(text="🥗 Обед", callback_data="meal_lunch")
        ],
        [
            InlineKeyboardButton(text="🍽 Ужин", callback_data="meal_dinner"),
            InlineKeyboardButton(text="🥪 Перекус", callback_data="meal_snack")
        ]
    ])
    return keyboard

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Create confirmation keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")
        ]
    ])
    return keyboard
