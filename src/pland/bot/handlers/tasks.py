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
task_analyzer = None
voice_handler = None

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

            # Преобразуем голосовое сообщение в текст
            text = await voice_handler.process_voice_message(message)

            if not text:
                logger.error("Не удалось преобразовать голосовое сообщение в текст")
                await processing_msg.edit_text(
                    "❌ Не удалось распознать голосовое сообщение.\n"
                    "Пожалуйста, попробуйте еще раз или отправьте текстовое сообщение."
                )
                return

            # Обновляем сообщение о процессе
            await processing_msg.edit_text(
                f"✅ Распознанный текст:\n{text}\n\n"
                "🤔 Анализирую сообщение..."
            )

            # Анализируем текст с помощью OpenAI
            analysis = await task_analyzer.analyze_task(text)

            if analysis:
                logger.info(f"Анализ успешно выполнен: {analysis}")
                await processing_msg.edit_text(
                    f"✅ Анализ выполнен:\n\n{analysis}"
                )
            else:
                logger.error("Не удалось выполнить анализ")
                await processing_msg.edit_text(
                    "🚫 Не удалось проанализировать сообщение.\n"
                    "Пожалуйста, попробуйте позже."
                )

        except Exception as e:
            logger.error(f"Ошибка при обработке голосового сообщения: {str(e)}", exc_info=True)
            error_message = "Произошла ошибка при обработке запроса."
            if Config.LOG_LEVEL == "DEBUG":
                error_message += f"\nДетали: {str(e)}"
            await processing_msg.edit_text(
                f"🚫 {error_message}\n"
                "Пожалуйста, попробуйте позже."
            )

    except Exception as e:
        logger.error(f"Ошибка в обработке сообщения: {str(e)}", exc_info=True)
        await message.answer(
            "🚫 Произошла ошибка при обработке сообщения.\n"
            "Пожалуйста, попробуйте позже."
        )

async def handle_text_message(message: Message, db: Database):
    """Обработка текстовых сообщений для анализа задач"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        logger.info(f"Получено сообщение от пользователя {username} (ID: {user_id})")
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

            # Проверяем подключение к API
            logger.debug("Проверяем подключение к OpenAI API...")
            is_connected = await task_analyzer.test_api_connection()
            if not is_connected:
                logger.error("Не удалось подключиться к OpenAI API")
                await processing_msg.edit_text(
                    "❌ Не удалось подключиться к OpenAI API.\n"
                    "Пожалуйста, попробуйте позже."
                )
                return

            logger.info(f"Начинаю анализ текста: '{message.text[:50]}...'")
            # Тестовый анализ текста
            analysis = await task_analyzer.analyze_task(message.text)

            if analysis:
                logger.info(f"Анализ успешно выполнен: {analysis}")
                await processing_msg.edit_text(
                    f"✅ Анализ выполнен:\n\n{analysis}"
                )
            else:
                logger.error("Не удалось выполнить анализ: результат пустой")
                await processing_msg.edit_text(
                    "🚫 Не удалось выполнить анализ.\n"
                    "Пожалуйста, попробуйте позже."
                )

        except Exception as e:
            logger.error(f"Ошибка при анализе: {str(e)}", exc_info=True)
            error_message = "Произошла ошибка при обработке запроса."
            if Config.LOG_LEVEL == "DEBUG":
                error_message += f"\nДетали: {str(e)}"
            await processing_msg.edit_text(
                f"🚫 {error_message}\n"
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
    logger.info("Регистрация обработчиков задач...")

    # Регистрируем обработчик текстовых сообщений
    router.message.register(
        lambda msg: handle_text_message(msg, db),
        F.text  # Простой фильтр для текстовых сообщений
    )

    # Регистрируем обработчик голосовых сообщений
    router.message.register(
        lambda msg: handle_voice_message(msg, db),
        F.voice  # Фильтр для голосовых сообщений
    )

    logger.info("✓ Обработчики сообщений зарегистрированы")