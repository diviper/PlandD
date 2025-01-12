"""Task-related message handlers"""
import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message

from src.database.database import Database
from src.services.ai import AIService

logger = logging.getLogger(__name__)

# Глобальный экземпляр сервиса
ai_service: AIService | None = None

async def handle_text_message(message: Message, db: Database):
    """Обработка текстовых сообщений для анализа задач"""
    try:
        if not message.text:
            await message.answer("Пожалуйста, отправьте текст задачи.")
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
    router.message.register(
        lambda msg, db=db: handle_text_message(msg, db),
        F.text
    )