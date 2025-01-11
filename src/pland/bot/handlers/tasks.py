"""Task-related message handlers"""
import logging
import traceback
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
    """Обработка текстовых сообщений для создания задач"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        logger.info(f"=== Начало обработки текстового сообщения ===")
        logger.info(f"От пользователя: {username} (ID: {user_id})")
        logger.debug(f"Текст сообщения: {message.text}")

        # Проверяем текст сообщения
        if not message.text:
            logger.warning("Получено пустое сообщение")
            await message.answer("Пожалуйста, отправьте текст задачи.")
            return

        # Проверяем длину и содержание сообщения
        if len(message.text.strip()) < 3 or message.text.strip().isdigit():
            logger.warning("Получено слишком короткое сообщение или просто число")
            await message.answer(
                "🤔 Пожалуйста, опишите задачу подробнее.\n"
                "Например: 'Подготовить презентацию к завтрашней встрече' или\n"
                "'Купить продукты для ужина'"
            )
            return

        # Отправляем сообщение о получении команды
        processing_msg = await message.answer("🤔 Анализирую вашу задачу...")

        try:
            # Инициализируем анализатор задач
            global task_analyzer
            if task_analyzer is None:
                logger.info("Инициализация TaskAnalyzer...")
                task_analyzer = TaskAnalyzer()

            # Анализируем задачу
            logger.info("Начало анализа задачи через OpenAI")
            analysis = await task_analyzer.analyze_task(message.text)
            logger.debug(f"Результат анализа: {analysis}")

            if not analysis:
                logger.error("Не получен результат анализа")
                await processing_msg.edit_text(
                    "🚫 Извините, не удалось проанализировать задачу.\n"
                    "Пожалуйста, попробуйте описать задачу другими словами."
                )
                return

            # Форматируем ответ пользователю
            priority_info = analysis["priority"]
            schedule_info = analysis["schedule"]
            resources_info = analysis["resources"]

            # Эмодзи для разных уровней приоритета
            priority_emoji = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }

            # Эмодзи для уровней фокусировки
            focus_emoji = {
                "high": "🎯",
                "medium": "👁",
                "low": "📝"
            }

            response = (
                f"📋 *Анализ задачи*\n\n"
                f"{priority_emoji.get(priority_info['level'], '⚪️')} *Приоритет:* {priority_info['level'].upper()}\n"
                f"├ {priority_info['reason']}\n"
                f"└ Срочность: {priority_info['urgency']}\n\n"
                f"⏰ *Расписание*\n"
                f"├ Оптимальное время: {schedule_info['optimal_time']}\n"
                f"├ Длительность: {schedule_info['estimated_duration']} мин\n"
                f"└ Дедлайн: {schedule_info['deadline']}\n\n"
                f"💪 *Ресурсы*\n"
                f"├ Энергозатратность: {resources_info['energy_required']}/10\n"
                f"└ {focus_emoji.get(resources_info['focus_level'], '📝')} Уровень фокусировки: {resources_info['focus_level'].upper()}\n"
            )

            if resources_info.get("materials"):
                response += "\n🔧 *Необходимые материалы:*\n"
                for material in resources_info["materials"]:
                    response += f"• {material}\n"

            logger.info("Отправка ответа пользователю")
            await processing_msg.edit_text(response, parse_mode="Markdown")
            logger.info("✓ Ответ успешно отправлен")

        except Exception as e:
            logger.error(f"Ошибка при анализе задачи: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                "🚫 Произошла ошибка при обработке задачи.\n"
                "Пожалуйста, попробуйте позже."
            )

    except Exception as e:
        logger.error(f"Критическая ошибка в обработке сообщения: {str(e)}", exc_info=True)
        logger.error(f"Traceback: {traceback.format_exc()}")
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
    logger.debug("Добавлен фильтр для текстовых сообщений не начинающихся с /")

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