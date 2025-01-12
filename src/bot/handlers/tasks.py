"""Task-related message handlers"""
import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message

from src.database.database import Database
from src.services.ai import AIService
from src.services.ai.nlp_processor import NLPProcessor

logger = logging.getLogger(__name__)

# Глобальные экземпляры сервисов
ai_service: AIService | None = None
nlp_processor: NLPProcessor | None = None

async def handle_text_message(message: Message, db: Database):
    """Обработка текстовых сообщений для анализа задач"""
    try:
        if not message.text:
            await message.answer("Пожалуйста, отправьте текст задачи.")
            return

        processing_msg = await message.answer("🤔 Анализирую сообщение...")

        # Инициализируем сервисы при первом использовании
        global ai_service, nlp_processor
        if ai_service is None:
            ai_service = AIService(db)
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

        # Анализируем задачу через AI сервис
        task_type = nlp_result.get('task_type', 'general')
        analysis = await ai_service.analyze_plan(message.text, task_type)
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

        # Получаем длительность из анализа AI
        duration = int(float(analysis.get('estimated_duration', 1)) * 24 * 60)  # конвертируем дни в минуты
        if time_info.get('duration'):
            duration = time_info['duration']

        # Формируем ответ пользователю
        response_parts = [
            f"✅ Я понял вашу задачу:\n",
            f"🎯 {analysis['title']}",
            f"⚡️ Приоритет: {analysis['priority']}",
            f"⏰ Время: {task_time.strftime('%H:%M')}",
            f"⌛️ Длительность: {duration} минут\n"
        ]

        if analysis.get('steps'):
            response_parts.append("📋 Шаги:")
            for i, step in enumerate(analysis['steps'], 1):
                response_parts.append(
                    f"{i}. {step['title']} ({int(float(step['duration']) * 24 * 60)} мин)"
                )
            response_parts.append("")

        if analysis.get('recommendations'):
            response_parts.append("💡 Рекомендации:")
            for rec in analysis['recommendations']:
                response_parts.append(f"  • {rec}")
            response_parts.append("")

        if analysis.get('potential_blockers'):
            response_parts.append("⚠️ Возможные препятствия:")
            for blocker in analysis['potential_blockers']:
                response_parts.append(f"  • {blocker}")
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
            priority=analysis['priority'].lower(),
            duration=duration,
            task_type=task_type,
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