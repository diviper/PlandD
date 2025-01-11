"""Task-related message handlers"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from pland.bot.keyboards import get_main_keyboard
from pland.database.database import Database
from pland.services.ai import TaskAnalyzer

logger = logging.getLogger(__name__)

# Глобальный экземпляр анализатора задач
task_analyzer = None

async def handle_text_message(message: Message, db: Database):
    """Обработка текстовых сообщений для тестирования связи с OpenAI"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        logger.info(f"=== Начало обработки текстового сообщения ===")
        logger.info(f"От пользователя: {username} (ID: {user_id})")
        logger.debug(f"Текст сообщения: {message.text}")

        # Проверяем текст сообщения
        if not message.text:
            logger.warning("Получено пустое сообщение")
            await message.answer("Пожалуйста, отправьте текст для анализа.")
            return

        # Отправляем сообщение о получении команды
        processing_msg = await message.answer("🤔 Проверяю связь с OpenAI API...")

        try:
            # Инициализируем анализатор задач
            global task_analyzer
            if task_analyzer is None:
                logger.info("Инициализация TaskAnalyzer...")
                task_analyzer = TaskAnalyzer()

            # Тестируем подключение
            is_connected = await task_analyzer.test_api_connection()
            if not is_connected:
                await processing_msg.edit_text(
                    "❌ Не удалось установить связь с OpenAI API.\n"
                    "Пожалуйста, попробуйте позже."
                )
                return

            # Анализируем задачу
            logger.info("Начало тестового анализа")
            analysis = await task_analyzer.analyze_task(message.text)
            logger.debug(f"Результат анализа: {analysis}")

            if not analysis:
                logger.error("Не получен результат анализа")
                await processing_msg.edit_text(
                    "🚫 Не удалось выполнить анализ.\n"
                    "Пожалуйста, попробуйте позже."
                )
                return

            # Отправляем простой ответ для тестирования
            response = (
                f"✅ Связь с OpenAI API работает!\n\n"
                f"Тестовый анализ текста:\n"
                f"{analysis}"
            )

            await processing_msg.edit_text(response)
            logger.info("✓ Тестовый ответ успешно отправлен")

        except Exception as e:
            logger.error(f"Ошибка при анализе: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                "🚫 Произошла ошибка при обработке запроса.\n"
                "Пожалуйста, попробуйте позже."
            )

    except Exception as e:
        logger.error(f"Критическая ошибка в обработке сообщения: {str(e)}", exc_info=True)
        await message.answer(
            "🚫 Произошла ошибка при обработке сообщения.\n"
            "Пожалуйста, попробуйте позже."
        )

def register_task_handlers(router: Router, db: Database):
    """Register task-related message handlers"""
    logger.info("=== Регистрация обработчиков задач ===")
    logger.debug(f"Регистрация в роутере: {router.name}")

    # Регистрируем обработчик текстовых сообщений
    router.message.register(
        lambda message: handle_text_message(message, db),
        F.content_type == "text",
        ~F.text.startswith("/")
    )
    logger.info("✓ Зарегистрирован обработчик текстовых сообщений")

    # Регистрируем обработчик команды /list
    router.message.register(
        lambda message: list_tasks(message, db),
        Command(commands=["list"])
    )
    logger.info("✓ Зарегистрирован обработчик команды /list")

    logger.info("=== Регистрация обработчиков задач завершена ===")
    logger.debug(f"Всего обработчиков в роутере: {len(router.message.handlers)}")

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

def _format_priority(priority: str) -> str:
    """Format priority for display"""
    priority_map = {
        "high": "Высокий ⚡️",
        "medium": "Средний ⚙️",
        "low": "Низкий 📝"
    }
    return priority_map.get(priority.lower(), "Средний ⚙️")

from pland.database.models import Task