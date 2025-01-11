"""Task-related message handlers"""
import logging
from aiogram import Router, F
from aiogram.types import Message

from pland.database.database import Database
from pland.services.ai import TaskAnalyzer
from pland.core.config import Config
from pland.services.voice.handler import VoiceHandler

logger = logging.getLogger(__name__)

# Глобальные экземпляры сервисов
task_analyzer: TaskAnalyzer | None = None
voice_handler: VoiceHandler | None = None

async def handle_text_message(message: Message, db: Database):
    """Обработка текстовых сообщений для анализа задач"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        logger.info(f"Получено текстовое сообщение от пользователя {username} (ID: {user_id})")
        logger.debug(f"Текст сообщения: {message.text}")

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
                logger.info("Инициализация TaskAnalyzer...")
                task_analyzer = TaskAnalyzer()
                logger.debug("TaskAnalyzer успешно инициализирован")

            # Анализируем текст с обработкой ошибок
            analysis = await task_analyzer.analyze_task(message.text)

            if not analysis:
                raise ValueError("Анализ вернул пустой результат")

            logger.info(f"Анализ успешно выполнен: {analysis}")
            # Форматируем ответ для пользователя
            response = (
                f"✅ Анализ задачи:\n\n"
                f"🎯 Приоритет: {analysis['priority']['level']}\n"
                f"🚨 Срочность: {analysis['priority']['urgency']}\n"
                f"⭐️ Важность: {analysis['priority']['importance']}\n"
                f"📝 Причина: {analysis['priority']['reason']}\n\n"
                f"📅 Расписание:\n"
                f"⏰ Оптимальное время: {analysis['schedule']['optimal_time']}\n"
                f"⌛️ Длительность: {analysis['schedule']['estimated_duration']} мин\n"
                f"🎯 Дедлайн: {analysis['schedule']['deadline']}\n"
                f"⚡️ Требуемая энергия: {analysis['resources']['energy_required']}/10\n\n"
                f"📋 Подзадачи:\n"
            )
            for task in analysis['schedule']['subtasks']:
                response += f"• {task['title']} ({task['duration']} мин)\n"

            await processing_msg.edit_text(response)
            logger.debug("Ответ успешно отправлен пользователю")

        except ValueError as ve:
            logger.error(f"Ошибка валидации: {str(ve)}")
            await processing_msg.edit_text(
                "🚫 Не удалось проанализировать сообщение.\n"
                "Пожалуйста, попробуйте переформулировать задачу."
            )

        except Exception as api_error:
            logger.error(f"Ошибка API: {str(api_error)}", exc_info=True)
            await processing_msg.edit_text(
                "🚫 Произошла ошибка при обработке запроса.\n"
                "Пожалуйста, попробуйте позже."
            )

    except Exception as e:
        logger.error(f"Критическая ошибка в обработке сообщения: {str(e)}", exc_info=True)
        try:
            await message.answer(
                "🚫 Произошла критическая ошибка при обработке сообщения.\n"
                "Пожалуйста, попробуйте позже."
            )
        except Exception as reply_error:
            logger.error(f"Не удалось отправить сообщение об ошибке: {str(reply_error)}")

async def handle_voice_message(message: Message, db: Database):
    """Обработка голосовых сообщений"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        logger.info(f"Получено голосовое сообщение от пользователя {username} (ID: {user_id})")

        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer("🎤 Обрабатываю голосовое сообщение...")

        try:
            # Инициализируем обработчик голосовых сообщений при первом использовании
            global voice_handler
            if voice_handler is None:
                logger.info("Инициализация VoiceHandler...")
                voice_handler = VoiceHandler(message.bot)
                logger.debug("VoiceHandler успешно инициализирован")

            # Преобразуем голосовое сообщение в текст с обработкой ошибок
            try:
                text = await voice_handler.process_voice_message(message)
                if not text:
                    raise ValueError("Не удалось распознать текст из голосового сообщения")

                # Обновляем сообщение о процессе
                await processing_msg.edit_text(
                    f"✅ Распознанный текст:\n{text}\n\n"
                    "🤔 Анализирую сообщение..."
                )

                # Инициализируем анализатор при необходимости
                global task_analyzer
                if task_analyzer is None:
                    logger.info("Инициализация TaskAnalyzer...")
                    task_analyzer = TaskAnalyzer()
                    logger.debug("TaskAnalyzer успешно инициализирован")

                # Анализируем текст
                analysis = await task_analyzer.analyze_task(text)
                if not analysis:
                    raise ValueError("Анализ вернул пустой результат")

                logger.info(f"Анализ успешно выполнен: {analysis}")
                # Форматируем ответ для пользователя
                response = (
                    f"✅ Анализ задачи:\n\n"
                    f"🎯 Приоритет: {analysis['priority']['level']}\n"
                    f"🚨 Срочность: {analysis['priority']['urgency']}\n"
                    f"⭐️ Важность: {analysis['priority']['importance']}\n"
                    f"📝 Причина: {analysis['priority']['reason']}\n\n"
                    f"📅 Расписание:\n"
                    f"⏰ Оптимальное время: {analysis['schedule']['optimal_time']}\n"
                    f"⌛️ Длительность: {analysis['schedule']['estimated_duration']} мин\n"
                    f"🎯 Дедлайн: {analysis['schedule']['deadline']}\n"
                    f"⚡️ Требуемая энергия: {analysis['resources']['energy_required']}/10\n\n"
                    f"📋 Подзадачи:\n"
                )
                for task in analysis['schedule']['subtasks']:
                    response += f"• {task['title']} ({task['duration']} мин)\n"

                await processing_msg.edit_text(response)
                logger.debug("Ответ успешно отправлен пользователю")

            except ValueError as ve:
                logger.error(f"Ошибка валидации: {str(ve)}")
                await processing_msg.edit_text(
                    "❌ Не удалось распознать голосовое сообщение.\n"
                    "Пожалуйста, попробуйте еще раз или отправьте текстовое сообщение."
                )

            except Exception as api_error:
                logger.error(f"Ошибка API: {str(api_error)}", exc_info=True)
                await processing_msg.edit_text(
                    "🚫 Произошла ошибка при обработке запроса.\n"
                    "Пожалуйста, попробуйте позже."
                )

        except Exception as e:
            logger.error(f"Ошибка при обработке голосового сообщения: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                "🚫 Произошла ошибка при обработке запроса.\n"
                "Пожалуйста, попробуйте позже."
            )

    except Exception as e:
        logger.error(f"Критическая ошибка в обработке сообщения: {str(e)}", exc_info=True)
        try:
            await message.answer(
                "🚫 Произошла критическая ошибка при обработке сообщения.\n"
                "Пожалуйста, попробуйте позже."
            )
        except Exception as reply_error:
            logger.error(f"Не удалось отправить сообщение об ошибке: {str(reply_error)}")

def register_task_handlers(router: Router, db: Database):
    """Register task-related message handlers"""
    try:
        logger.info("Регистрация обработчиков задач...")

        # Регистрируем обработчик текстовых сообщений
        async def text_handler(message: Message):
            await handle_text_message(message, db)

        # Регистрируем обработчик голосовых сообщений
        async def voice_handler(message: Message):
            await handle_voice_message(message, db)

        # Регистрируем обработчики с фильтрами
        router.message.register(text_handler, F.content_type.in_({"text"}))
        router.message.register(voice_handler, F.content_type.in_({"voice"}))

        logger.info("✓ Обработчики сообщений зарегистрированы")
    except Exception as e:
        logger.error(f"Ошибка при регистрации обработчиков: {str(e)}", exc_info=True)
        raise