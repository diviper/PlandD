"""Task-related message handlers"""
import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message

from src.database.database import Database
from src.services.ai import TaskAnalyzer
from src.services.ai.nlp_processor import NLPProcessor

logger = logging.getLogger(__name__)

# Глобальные экземпляры сервисов
task_analyzer: TaskAnalyzer | None = None
nlp_processor: NLPProcessor | None = None

async def handle_text_message(message: Message, db: Database):
    """Обработка текстовых сообщений для анализа задач"""
    try:
        if not message.text:
            await message.answer("Пожалуйста, отправьте текст задачи.")
            return

        processing_msg = await message.answer("🤔 Анализирую сообщение...")

        # Инициализируем сервисы при первом использовании
        global task_analyzer, nlp_processor
        if task_analyzer is None:
            task_analyzer = TaskAnalyzer()
        if nlp_processor is None:
            nlp_processor = NLPProcessor()

        # Обрабатываем текст через NLP
        nlp_result = await nlp_processor.process_message(message.text)
        if not nlp_result:
            await message.answer(
                "❌ Извините, я не смог правильно понять ваше сообщение.\n"
                "Попробуйте описать задачу более подробно."
            )
            return

        # Анализируем задачу
        analysis = await task_analyzer.analyze_task(message.text)
        if not analysis:
            await message.answer(
                "❌ Не удалось проанализировать задачу.\n"
                "Пожалуйста, попробуйте переформулировать."
            )
            return

        # Формируем время выполнения на основе NLP анализа
        time_info = nlp_result.get('time_info', {})
        task_time = None

        if time_info.get('explicit_time'):
            # Если указано конкретное время
            task_time = datetime.combine(
                datetime.now().date(),
                time_info['explicit_time']
            )
        elif time_info.get('relative_time'):
            # Если указано относительное время
            task_time = datetime.now() + time_info['relative_time']
        else:
            # По умолчанию ставим на следующий час
            task_time = datetime.now().replace(
                minute=0,
                second=0,
                microsecond=0
            ) + timedelta(hours=1)

        # Обновляем длительность задачи если она указана в сообщении
        if time_info.get('duration'):
            analysis['duration'] = time_info['duration']

        # Формируем ответ пользователю
        response_parts = [
            f"✅ Я понял вашу задачу:\n",
            f"🎯 Тип: {nlp_result.get('task_type', 'Не указан')}",
            f"⚡️ Приоритет: {analysis['priority']}",
            f"⏰ Время: {task_time.strftime('%H:%M')}",
            f"⌛️ Длительность: {analysis['duration']} минут\n"
        ]

        if nlp_result.get('required_resources'):
            response_parts.append("🛠 Потребуется:")
            for resource in nlp_result['required_resources']:
                response_parts.append(f"  • {resource}")
            response_parts.append("")

        if analysis.get('subtasks'):
            response_parts.append("📋 Подзадачи:")
            for i, subtask in enumerate(analysis['subtasks'], 1):
                response_parts.append(
                    f"{i}. {subtask['title']} ({subtask['duration']} мин)"
                )
            response_parts.append("")

        if nlp_result.get('dependencies'):
            response_parts.append("🔄 Зависимости:")
            for dep in nlp_result['dependencies']:
                response_parts.append(f"  • {dep}")
            response_parts.append("")

        # Добавляем оценку сложности
        complexity = nlp_result.get('complexity', 5)
        response_parts.append(
            f"📊 Сложность: {'🟦' * ((complexity + 1) // 2)} ({complexity}/10)"
        )

        await processing_msg.delete()
        await message.answer("\n".join(response_parts))

        # Сохраняем задачу в базу данных
        await db.add_task(
            user_id=message.from_user.id,
            text=message.text,
            deadline=task_time,
            priority=analysis['priority'],
            duration=analysis['duration'],
            task_type=nlp_result.get('task_type'),
            complexity=complexity
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {str(e)}", exc_info=True)
        await message.answer(
            "🚫 Произошла ошибка при обработке сообщения.\n"
            "Пожалуйста, попробуйте позже."
        )

def register_task_handlers(router: Router, db: Database):
    """Регистрация обработчиков задач"""
    router.message.register(
        lambda msg: handle_text_message(msg, db),
        F.text
    )