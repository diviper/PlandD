"""Task-related message handlers"""
import logging
from aiogram import Router, F
from aiogram.types import Message

from pland.database.database import Database
from pland.services.ai import TaskAnalyzer

logger = logging.getLogger(__name__)

# Глобальный экземпляр анализатора задач
task_analyzer = None

async def handle_text_message(message: Message, db: Database):
    """Обработка текстовых сообщений для тестирования связи с OpenAI"""
    try:
        # Проверяем текст сообщения
        if not message.text:
            await message.answer("Пожалуйста, отправьте текст для анализа.")
            return

        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer("🤔 Анализирую сообщение...")

        try:
            # Инициализируем анализатор задач при первом использовании
            global task_analyzer
            if task_analyzer is None:
                task_analyzer = TaskAnalyzer()

            # Проверяем подключение к API
            is_connected = await task_analyzer.test_api_connection()
            if not is_connected:
                await processing_msg.edit_text(
                    "❌ Не удалось подключиться к OpenAI API.\n"
                    "Пожалуйста, попробуйте позже."
                )
                return

            # Тестовый анализ текста
            analysis = await task_analyzer.analyze_task(message.text)

            if analysis:
                await processing_msg.edit_text(
                    f"✅ Анализ выполнен:\n\n{analysis}"
                )
            else:
                await processing_msg.edit_text(
                    "🚫 Не удалось выполнить анализ.\n"
                    "Пожалуйста, попробуйте позже."
                )

        except Exception as e:
            logger.error(f"Ошибка при анализе: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                "🚫 Произошла ошибка при обработке запроса.\n"
                "Пожалуйста, попробуйте позже."
            )

    except Exception as e:
        logger.error(f"Ошибка в обработке сообщения: {str(e)}", exc_info=True)
        await message.answer(
            "🚫 Произошла ошибка при обработке сообщения.\n"
            "Пожалуйста, попробуйте позже."
        )

def register_task_handlers(router: Router, db: Database):
    """Register task-related message handlers"""
    # Регистрируем только обработчик текстовых сообщений
    router.message.register(
        lambda message: handle_text_message(message, db),
        F.content_type == "text",
        ~F.text.startswith("/")
    )