"""Task-related message handlers"""
import logging
from aiogram import Router, F
from aiogram.types import Message

from src.database.database import Database
from src.services.ai import TaskAnalyzer

logger = logging.getLogger(__name__)

# Глобальный экземпляр анализатора
task_analyzer: TaskAnalyzer | None = None

async def handle_text_message(message: Message, db: Database):
    """Обработка текстовых сообщений для анализа задач"""
    try:
        if not message.text:
            await message.answer("Пожалуйста, отправьте текст задачи.")
            return

        processing_msg = await message.answer("🤔 Анализирую задачу...")

        global task_analyzer
        if task_analyzer is None:
            task_analyzer = TaskAnalyzer()

        analysis = await task_analyzer.analyze_task(message.text)
        if not analysis:
            await message.answer("❌ Не удалось проанализировать задачу. Попробуйте переформулировать.")
            return

        response = (
            f"✅ План выполнения задачи:\n\n"
            f"🎯 Приоритет: {analysis['priority']}\n"
            f"⏰ Дедлайн: {analysis['deadline']}\n"
            f"⌛️ Длительность: {analysis['duration']} минут\n\n"
            f"📋 Подзадачи:\n"
        )

        for i, subtask in enumerate(analysis['subtasks'], 1):
            response += f"{i}. {subtask['title']} ({subtask['duration']} мин)\n"

        await processing_msg.delete()
        await message.answer(response)

        # Сохраняем задачу в базу данных
        await db.add_task(
            user_id=message.from_user.id,
            text=message.text,
            deadline=analysis['deadline'],
            priority=analysis['priority']
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {str(e)}", exc_info=True)
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

def register_task_handlers(router: Router, db: Database):
    """Register task-related message handlers"""
    router.message.register(
        lambda msg, db=db: handle_text_message(msg, db),
        F.text
    )