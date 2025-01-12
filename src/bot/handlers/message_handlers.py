"""Message handlers for the Telegram bot"""
import logging
from datetime import datetime
from typing import Optional, Dict

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from src.database.database import Database
from src.services.ai.analyzer import TaskAnalyzer
from src.services.ai.planner import TaskPlanner

logger = logging.getLogger(__name__)

class MessageHandlers:
    """Обработчики сообщений для Telegram бота"""

    def __init__(self, router: Router, db: Database):
        """Initialize message handlers with router and database"""
        self.router = router
        self.db = db
        self.analyzer = TaskAnalyzer()
        self.planner = TaskPlanner()
        self._register_handlers()

    def _register_handlers(self):
        """Register all message handlers"""
        self.router.message.register(self.handle_start, Command("start"))
        self.router.message.register(self.handle_help, Command("help"))
        self.router.message.register(self.handle_settings, Command("settings"))
        self.router.message.register(self.handle_stats, Command("stats"))
        self.router.message.register(self.handle_message, F.text)

    async def handle_start(self, message: Message):
        """Handle /start command"""
        await message.answer(
            "👋 Привет! Я твой персональный AI-планировщик.\n\n"
            "🎯 Я помогу тебе:\n"
            "- Анализировать и планировать задачи\n"
            "- Оптимизировать расписание\n"
            "- Отслеживать прогресс\n\n"
            "💡 Просто напиши мне о своих планах или задачах!"
        )

    async def handle_help(self, message: Message):
        """Handle /help command"""
        await message.answer(
            "🔍 <b>Основные команды:</b>\n\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/settings - Настройки планирования\n"
            "/stats - Статистика и прогресс\n\n"
            "✨ Просто пиши мне о своих задачах, и я помогу их организовать!"
        )

    async def handle_settings(self, message: Message):
        """Handle /settings command"""
        # TODO: Implement settings management
        await message.answer(
            "⚙️ <b>Настройки:</b>\n\n"
            "🕒 Предпочтительное время для задач\n"
            "📊 Уровень детализации планов\n"
            "🔔 Настройки уведомлений\n\n"
            "🚧 Эта функция находится в разработке..."
        )

    async def handle_stats(self, message: Message):
        """Handle /stats command"""
        # TODO: Implement statistics tracking
        await message.answer(
            "📊 <b>Статистика пока недоступна</b>\n\n"
            "🚧 Мы работаем над этой функцией..."
        )

    async def handle_message(self, message: Message):
        """Handle regular text messages"""
        try:
            user_id = message.from_user.id
            current_time = datetime.now()

            # Анализируем сообщение через AI
            analysis_result = await self.analyzer.analyze_task(message.text)
            if not analysis_result:
                await message.answer(
                    "🤔 Извини, я не смог понять задачу.\n"
                    "Попробуй описать её подробнее или по-другому."
                )
                return

            # Получаем текущее расписание пользователя
            user_schedule = await self.db.get_user_schedule(user_id)
            
            # Получаем или устанавливаем уровень энергии по умолчанию
            energy_level = await self.db.get_user_energy_level(user_id) or 7

            # Оптимизируем расписание с учетом новой задачи
            tasks = await self.db.get_user_tasks(user_id)
            tasks.append({
                "id": len(tasks) + 1,
                "title": message.text,
                "priority": analysis_result.get("priority", "medium"),
                "estimated_duration": analysis_result.get("duration", 30),
                "due_date": datetime.strptime(
                    analysis_result.get("deadline"),
                    "%Y-%m-%d %H:%M"
                ),
                "subtasks": analysis_result.get("subtasks", [])
            })

            optimized_tasks, warnings = await self.planner.optimize_schedule(
                tasks=tasks,
                user_schedule=user_schedule,
                energy_level=energy_level
            )

            # Сохраняем обновленное расписание
            await self.db.update_user_tasks(user_id, optimized_tasks)

            # Формируем ответ пользователю
            response = [
                "✅ <b>Задача добавлена в расписание!</b>\n",
                f"🎯 Приоритет: {analysis_result['priority']}",
                f"⏰ Дедлайн: {analysis_result['deadline']}",
                f"⌛️ Оценка длительности: {analysis_result['duration']} минут\n"
            ]

            if analysis_result.get("subtasks"):
                response.append("📋 <b>Подзадачи:</b>")
                for subtask in analysis_result["subtasks"]:
                    response.append(f"• {subtask['title']} (~{subtask['duration']} мин)")
                response.append("")

            if warnings:
                response.append("⚠️ <b>Важные замечания:</b>")
                for warning in warnings:
                    response.append(f"• {warning}")

            await message.answer("\n".join(response))

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}", exc_info=True)
            await message.answer(
                "😓 Произошла ошибка при обработке сообщения.\n"
                "Пожалуйста, попробуйте позже."
            )

def register_handlers(router: Router, db: Database):
    """Register all message handlers"""
    MessageHandlers(router, db)
