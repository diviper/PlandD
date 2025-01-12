"""Task-related message handlers"""
import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext

from src.database.database import Database
from src.services.ai import AIService
from src.bot.handlers.plan_handler import PlanStates

logger = logging.getLogger(__name__)

# Глобальный экземпляр сервиса
ai_service: AIService | None = None

# Список кнопок меню
MENU_BUTTONS = {
    "📝 Новый план",
    "📋 Мои планы",
    "📊 Прогресс",
    "⚙️ Настройки",
    "❓ Помощь"
}

async def handle_text_message(message: Message, state: FSMContext, db: Database):
    """Обработка текстовых сообщений для анализа задач"""
    try:
        if not message.text:
            await message.answer("Пожалуйста, отправьте текст задачи.")
            return

        # Проверяем состояние
        current_state = await state.get_state()
        if current_state is not None:
            # Если есть активное состояние, пропускаем обработку
            return

        # Инициализируем AI сервис, если он еще не создан
        global ai_service
        if ai_service is None:
            ai_service = AIService(db)

        # Анализируем текст задачи
        task_analysis = await ai_service.analyze_text(message.text)
        if not task_analysis:
            await message.answer("*burp* Что-то пошло не так при анализе задачи, Морти!")
            return

        # Анализируем план
        plan_analysis = await ai_service.analyze_plan(message.text)

        # Генерируем ответ в стиле Рика
        context = {
            "task_analysis": task_analysis,
            "plan_analysis": plan_analysis
        }
        response = await ai_service.generate_response(context)

        await message.answer(response, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await message.answer(
            "Уупс, Морти! *burp* Произошла какая-то квантовая аномалия!\n"
            "Давай попробуем еще раз, только в этот раз без всяких там парадоксов!"
        )

def register_task_handlers(router: Router, db: Database):
    """Регистрация обработчиков задач"""
    # Создаем обработчик для текстовых сообщений
    async def wrapped_handle_text_message(message: Message, state: FSMContext):
        await handle_text_message(message, state, db)
    
    # Регистрируем обработчик для всех текстовых сообщений, 
    # кроме команд, кнопок меню и состояний планов
    router.message.register(
        wrapped_handle_text_message,
        ~Command(commands=["start", "help", "plan", "settings", "stats"]),  # Исключаем команды
        lambda message: message.text not in MENU_BUTTONS  # Исключаем кнопки меню
    )