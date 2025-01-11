"""Task-related message handlers"""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from pland.bot.keyboards import get_main_keyboard
from pland.core.config import Config
from pland.database.database import Database
from pland.database.models import Task
from pland.services.ai import TaskAnalyzer

logger = logging.getLogger(__name__)

# Глобальный экземпляр анализатора задач
task_analyzer = None

async def init_task_analyzer():
    """Initialize task analyzer and test connection"""
    global task_analyzer
    if task_analyzer is None:
        try:
            logger.info("Initializing TaskAnalyzer...")
            task_analyzer = TaskAnalyzer()
            if not await task_analyzer.test_api_connection():
                logger.error("Failed to connect to OpenAI API")
                raise Exception("OpenAI API connection failed")
            logger.info("TaskAnalyzer successfully initialized")
        except Exception as e:
            logger.error(f"Error initializing TaskAnalyzer: {str(e)}", exc_info=True)
            raise
    return task_analyzer

async def handle_text_message(message: Message, db: Database):
    """Обработка текстовых сообщений для создания задач"""
    try:
        user_id = message.from_user.id
        logger.info(f"=== Starting text message processing ===")
        logger.info(f"From user: {user_id}")
        logger.debug(f"Message text: {message.text}")

        if not message.text:
            await message.answer("Пожалуйста, отправьте текст задачи.")
            return

        if message.text.startswith('/'):
            return

        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer(
            "🤔 Анализирую вашу задачу...\n"
            "Это может занять несколько секунд."
        )

        try:
            # Инициализируем анализатор задач
            logger.info("Initializing task analyzer...")
            analyzer = await init_task_analyzer()
            logger.info("Task analyzer initialized successfully")

            # Анализируем задачу
            logger.info("Starting task analysis through OpenAI")
            analysis = await analyzer.analyze_task(message.text)
            logger.debug(f"Analysis result: {analysis}")

            if not analysis:
                logger.error("No analysis result received from OpenAI")
                await processing_msg.edit_text(
                    "🚫 Извините, я не смог правильно проанализировать задачу.\n"
                    "Пожалуйста, попробуйте описать задачу более подробно или другими словами."
                )
                return

            logger.info("Task analysis completed successfully")

            # Создаем задачу
            task = Task(
                id=None,
                user_id=user_id,
                title=analysis.get('title', 'Новая задача'),
                description=message.text,
                priority=analysis.get('priority', 'medium'),
                due_date=analysis.get('due_date', datetime.now()),
                completed=False,
                estimated_duration=analysis.get('estimated_total_time', 30),
                energy_level=analysis.get('energy_level', 5)
            )

            # Сохраняем задачу в базу данных
            task_id = db.add_task(task)
            logger.info(f"Task saved with ID: {task_id}")

            # Форматируем информацию о подзадачах
            subtasks_info = ""
            if 'tasks' in analysis and analysis['tasks']:
                subtasks_info = "\n📋 Подзадачи:\n" + "\n".join([
                    f"• {task['title']} "
                    f"(⚡️{task.get('energy_level', 5)}/10, "
                    f"⏱{task.get('estimated_duration', 15)} мин)"
                    for task in analysis['tasks']
                ])

            # Форматируем ответ пользователю
            response = (
                f"✅ Задача создана!\n\n"
                f"📌 {task.title}\n"
                f"⚡️ Приоритет: {_format_priority(task.priority)}\n"
                f"🕒 Срок: {task.due_date.strftime('%d.%m.%Y %H:%M')}\n"
                f"⏱ Общее время: {task.estimated_duration} мин\n"
                f"{subtasks_info}\n\n"
                f"❓ Хотите изменить задачу? Используйте /edit_{task_id}"
            )

            await processing_msg.edit_text(response)
            logger.info("Response sent to user successfully")

        except Exception as e:
            logger.error(f"Error during task analysis: {str(e)}", exc_info=True)
            error_message = (
                "🚫 Произошла ошибка при обработке задачи.\n"
                "Пожалуйста, попробуйте позже или переформулируйте задачу."
            )
            await processing_msg.edit_text(error_message)

    except Exception as e:
        logger.error(f"Critical error in message processing: {str(e)}", exc_info=True)
        await message.answer(
            "🚫 Произошла ошибка при обработке сообщения.\n"
            "Пожалуйста, попробуйте позже."
        )

    finally:
        logger.info("=== Text message processing completed ===")

def _format_priority(priority: str) -> str:
    """Format priority for display"""
    priority_map = {
        "high": "Высокий ⚡️",
        "medium": "Средний ⚙️",
        "low": "Низкий 📝"
    }
    return priority_map.get(priority.lower(), "Средний ⚙️")

def register_task_handlers(router: Router, db: Database):
    """Register task-related message handlers"""
    logger.info("Registering task handlers...")

    # Text message handler
    router.message.register(
        lambda message: handle_text_message(message, db),
        F.content_type == "text",
        ~F.text.startswith("/")
    )

    # /list command handler
    router.message.register(
        lambda message: list_tasks(message, db),
        Command(commands=["list"])
    )

    logger.info("✓ Task handlers registered successfully")

async def list_tasks(message: Message, db: Database):
    """Show list of user's tasks"""
    tasks = db.get_tasks(message.from_user.id)
    if not tasks:
        await message.answer(
            "📝 У вас пока нет задач.",
            reply_markup=get_main_keyboard()
        )
        return

    tasks_text = "📋 Ваши задачи:\n\n"
    for task in tasks:
        status = "✅" if task.completed else "⏳"
        tasks_text += (
            f"{status} {task.title}\n"
            f"⚡️ Приоритет: {_format_priority(task.priority)}\n"
            f"🕒 До: {task.due_date.strftime('%d.%m.%Y %H:%M')}\n\n"
        )

    await message.answer(tasks_text, reply_markup=get_main_keyboard())

async def ensure_reminder_settings(user_id: int, db: Database) -> None:
    """Проверка и создание настроек напоминаний для пользователя"""
    settings = db.get_reminder_settings(user_id)
    if not settings:
        # Создаем настройки по умолчанию
        default_settings = ReminderSettings(
            id=None,
            user_id=user_id,
            default_reminder_time=30,
            morning_reminder_time="09:00",
            evening_reminder_time="20:00",
            priority_high_interval=30,
            priority_medium_interval=60,
            priority_low_interval=120,
            quiet_hours_start="23:00",
            quiet_hours_end="07:00",
            reminder_types=["all"]  # Включаем все типы напоминаний по умолчанию
        )
        db.update_reminder_settings(default_settings)
        logger.info(f"Созданы настройки напоминаний по умолчанию для пользователя {user_id}")

async def handle_voice_message(message: Message, db: Database):
    """Обработка голосовых сообщений для создания задач"""
    try:
        user_id = message.from_user.id
        logger.info(f"Получено голосовое сообщение от пользователя {user_id}")

        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer("🎤 Обрабатываю голосовое сообщение...")

        # Получаем информацию о файле
        voice: Voice = message.voice
        if not voice:
            await processing_msg.edit_text("❌ Ошибка: голосовое сообщение не найдено")
            return

        # Получаем URL файла для загрузки
        file = await message.bot.get_file(voice.file_id)
        file_url = file.file_url  # Используем прямой URL файла

        # Обрабатываем голосовое сообщение
        success, text = await voice_handler.process_voice_message(file_url, voice.file_id)

        if not success or not text:
            await processing_msg.edit_text(
                "❌ Не удалось обработать голосовое сообщение. "
                "Пожалуйста, попробуйте ещё раз или отправьте текст."
            )
            return

        await processing_msg.edit_text(
            f"✅ Текст из голосового сообщения:\n\n"
            f"{text}\n\n"
            f"🤔 Анализирую задачу..."
        )

        # Анализируем задачу и создаем её
        await analyze_and_create_tasks(text, user_id, db, processing_msg)

    except Exception as e:
        logger.error(f"Ошибка при обработке голосового сообщения: {str(e)}", exc_info=True)
        if message:
            await message.answer(
                "Произошла ошибка при обработке голосового сообщения. "
                "Пожалуйста, попробуйте позже или отправьте текст."
            )

async def analyze_and_create_tasks(text: str, user_id: int, db: Database, message: Message):
    """Анализ текста и создание задач"""
    try:
        logger.debug(f"Начинаем анализ задачи для пользователя {user_id}")
        analyzer = await init_task_analyzer()
        analysis = await analyzer.analyze_task(text)
        logger.debug(f"Получен результат анализа: {analysis}")

        # Создаем основную задачу
        main_task = Task(
            id=None,
            user_id=user_id,
            title=analysis['title'],
            description=text,
            priority=analysis['priority'],
            due_date=analysis['due_date'],
            completed=False
        )
        main_task_id = db.add_task(main_task)

        # Создаем подзадачи
        subtask_ids = []
        for task in analysis['tasks']:
            subtask = Task(
                id=None,
                user_id=user_id,
                title=task['title'],
                description=f"Часть задачи: {analysis['title']}",
                priority=task['priority'],
                due_date=analysis['due_date'],
                parent_task_id=main_task_id,
                completed=False,
                estimated_duration=task['estimated_duration'],
                energy_level=task['energy_level'],
                category=task['category']
            )
            subtask_id = db.add_task(subtask)
            subtask_ids.append(subtask_id)

        # Формируем сообщение с результатами анализа
        tasks_info = "\n".join([
            f"• {task['title']} "
            f"(⚡️{task['energy_level']}/10, ⏱{task['estimated_duration']} мин)"
            for task in analysis['tasks']
        ])

        schedule_info = (
            f"📋 Задачи:\n{tasks_info}\n\n"
            f"⚠️ Причина приоритета: {analysis['priority_reason']}\n"
            f"📝 Рекомендуемый порядок выполнения:\n"
            f"{', '.join(str(i+1) for i in analysis['suggested_order'])}"
        )

        await message.edit_text(
            f"✅ Ситуация проанализирована!\n\n"
            f"📌 Общая задача: {main_task.title}\n"
            f"⚡️ Приоритет: {_format_priority(main_task.priority)}\n"
            f"🕒 Крайний срок: {main_task.due_date.strftime(Config.DATETIME_FORMAT)}\n\n"
            f"{schedule_info}\n\n"
            f"❓ Всё верно? Если нет, используйте команду /edit_{main_task_id} для редактирования"
        )

    except Exception as e:
        logger.error(f"Ошибка при анализе и создании задач: {str(e)}", exc_info=True)
        raise

class TaskStates(StatesGroup):
    """States for task creation and editing process"""
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_priority = State()
    waiting_for_due_date = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()

async def add_task_start(message: Message, state: FSMContext):
    """Start task creation process"""
    try:
        logger.info(f"Начат процесс создания задачи пользователем {message.from_user.id}")
        await state.set_state(TaskStates.waiting_for_title)
        await message.answer("📝 Введите название задачи:")
    except Exception as e:
        logger.error(f"Ошибка при начале создания задачи: {str(e)}", exc_info=True)
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
        await state.clear()

from pland.services.voice_handler import VoiceHandler
voice_handler = VoiceHandler()

from pland.database.models import ReminderSettings