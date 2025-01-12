"""Telegram bot keyboard layouts"""
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает основную клавиатуру бота."""
    keyboard = [
        [KeyboardButton(text="📝 Новый план")],
        [KeyboardButton(text="📋 Мои планы"), KeyboardButton(text="📊 Прогресс")],
        [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True
    )

def get_plan_type_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора типа плана"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎯 Личная цель", callback_data="plan_personal"),
            InlineKeyboardButton(text="💼 Рабочий проект", callback_data="plan_work")
        ],
        [
            InlineKeyboardButton(text="📚 Обучение", callback_data="plan_study"),
            InlineKeyboardButton(text="🏃 Спорт/Здоровье", callback_data="plan_health")
        ]
    ])
    return keyboard

def get_priority_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора приоритета"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔴 Высокий", callback_data="priority_high"),
            InlineKeyboardButton(text="🟡 Средний", callback_data="priority_medium"),
            InlineKeyboardButton(text="🟢 Низкий", callback_data="priority_low")
        ]
    ])
    return keyboard

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для подтверждения"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes"),
            InlineKeyboardButton(text="🔄 Изменить", callback_data="confirm_edit"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="confirm_cancel")
        ]
    ])
    return keyboard

def get_plan_actions_keyboard(plan_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру действий с планом"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"plan_edit_{plan_id}"),
            InlineKeyboardButton(text="✅ Отметить прогресс", callback_data=f"plan_progress_{plan_id}")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data=f"plan_stats_{plan_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"plan_delete_{plan_id}")
        ]
    ])
    return keyboard
