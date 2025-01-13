"""Main bot file"""

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from src.config import BOT_TOKEN
from src.bot.handlers.plan_handler import register_plan_handlers
from src.services.plan_service import PlanService
from src.services.ai_service import AIService
from src.database.database import SessionLocal

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создание сессии базы данных
db = SessionLocal()

# Инициализация сервисов
plan_service = PlanService(db)
ai_service = AIService()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("📝 Новый план"))
    keyboard.add(types.KeyboardButton("📋 Мои планы"))

    await message.answer(
        "Привет, мешок с костями! 🦴\n\n"
        "Я твой персональный планировщик задач в стиле Рика из 'Рик и Морти'! *burp* 🥒\n\n"
        "Вот что я могу:\n"
        "• /plan - создать новый план\n"
        "• /help - получить помощь\n\n"
        "Давай начнем планировать что-нибудь безумное! 🚀",
        reply_markup=keyboard
    )

@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.answer(
        "Вот что я умею, Морти! *burp* 🥒\n\n"
        "📝 Основные команды:\n"
        "• /plan - создать новый план\n"
        "• /help - получить помощь\n\n"
        "Давай начнем планировать что-нибудь безумное! 🚀"
    )

@dp.message_handler(lambda message: message.text == "📝 Новый план")
async def button_new_plan(message: types.Message):
    """Обработчик кнопки Новый план"""
    await message.answer(
        "Отлично! Давай создадим новый план! *burp* 🥒\n\n"
        "Просто напиши мне свой план, и я помогу тебе его оптимизировать!"
    )

@dp.message_handler(lambda message: message.text == "📋 Мои планы")
async def button_my_plans(message: types.Message):
    """Обработчик кнопки Мои планы"""
    plans = await plan_service.get_user_plans(message.from_user.id)
    
    if not plans:
        await message.answer(
            "У тебя пока нет планов, Морти! *burp* 🥒\n"
            "Используй /plan чтобы создать новый план!"
        )
        return
        
    text = "Вот твои планы, Морти! *burp* 🥒\n\n"
    for plan in plans:
        text += f"📌 {plan.title}\n"
        text += f"⏰ {plan.start_time.strftime('%H:%M')} - {plan.end_time.strftime('%H:%M')}\n"
        text += f"📝 {plan.description}\n\n"
        
    await message.answer(text)

def register_handlers():
    """Регистрация всех обработчиков"""
    register_plan_handlers(dp, plan_service, ai_service)

async def on_startup(dp):
    """Действия при запуске бота"""
    register_handlers()

def main():
    """Запуск бота"""
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

if __name__ == '__main__':
    main()
