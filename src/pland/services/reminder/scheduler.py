"""Scheduler service for task reminders"""
import logging
from datetime import datetime, timedelta
import json

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from pland.core.config import Config
from pland.database.database import Database

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Планировщик напоминаний и уведомлений"""

    def __init__(self, bot: Bot, db: Database):
        """
        Инициализация планировщика

        :param bot: Экземпляр бота для отправки сообщений
        :param db: Экземпляр базы данных для получения задач
        """
        self.bot = bot
        self.db = db
        self.scheduler = AsyncIOScheduler()
        # Базовые интервалы напоминаний для разных приоритетов (в минутах)
        self._reminder_intervals = {
            Config.PRIORITY_HIGH: 30,    # Каждые 30 минут для высокого приоритета
            Config.PRIORITY_MEDIUM: 60,  # Каждый час для среднего приоритета
            Config.PRIORITY_LOW: 120     # Каждые 2 часа для низкого приоритета
        }
        # Форматы сообщений для разных типов напоминаний
        self._message_formats = {
            "task_reminder": "🔔 Напоминание о задаче:\n{task_title}\n⏰ До выполнения: {time_left}",
            "energy_warning": "⚡️ Внимание! Задача '{task_title}' требует высокого уровня энергии ({energy_level}/10).\nРекомендуемое время: {optimal_time}",
            "urgent_reminder": "🚨 Срочная задача!\n{task_title}\nОсталось времени: {time_left}"
        }

    def start(self):
        """Запуск планировщика"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Планировщик напоминаний запущен")
            self._schedule_daily_jobs()
            self._schedule_energy_based_reminders()

    def stop(self):
        """Остановка планировщика"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Планировщик напоминаний остановлен")

    def _schedule_daily_jobs(self):
        """Настройка ежедневных задач с учетом пользовательских настроек"""
        # Для каждого пользователя настраиваем индивидуальное расписание
        for task in self.db.get_all_tasks():
            user_id = task.user_id
            settings = self.db.get_reminder_settings(user_id)

            if not settings:
                continue  # Пропускаем, если нет настроек

            # Утренняя сводка задач с учетом энергозатрат
            self.scheduler.add_job(
                self._send_daily_summary,
                CronTrigger(
                    hour=int(settings.morning_reminder_time.split(":")[0]),
                    minute=int(settings.morning_reminder_time.split(":")[1])
                ),
                args=[user_id],
                id=f"morning_summary_{user_id}",
                replace_existing=True
            )

            # Вечерний анализ выполнения и планирование следующего дня
            self.scheduler.add_job(
                self._send_evening_summary,
                CronTrigger(
                    hour=int(settings.evening_reminder_time.split(":")[0]),
                    minute=int(settings.evening_reminder_time.split(":")[1])
                ),
                args=[user_id],
                id=f"evening_summary_{user_id}",
                replace_existing=True
            )

            # Настраиваем интервалы напоминаний с учетом приоритетов и настроек пользователя
            self._schedule_priority_based_reminders(user_id, settings)

    def _schedule_priority_based_reminders(self, user_id: int, settings):
        """Настройка напоминаний на основе приоритетов"""
        intervals = {
            Config.PRIORITY_HIGH: settings.priority_high_interval,
            Config.PRIORITY_MEDIUM: settings.priority_medium_interval,
            Config.PRIORITY_LOW: settings.priority_low_interval
        }

        for priority, interval in intervals.items():
            self.scheduler.add_job(
                self._check_upcoming_tasks,
                IntervalTrigger(minutes=interval),
                args=[user_id, priority],
                id=f"check_tasks_{user_id}_{priority}",
                replace_existing=True
            )

    def _schedule_energy_based_reminders(self):
        """Планирование напоминаний с учетом энергозатрат задач"""
        self.scheduler.add_job(
            self._check_energy_levels,
            IntervalTrigger(hours=1),
            id="energy_check",
            replace_existing=True
        )

    async def _check_energy_levels(self):
        """Проверка энергозатратных задач и отправка рекомендаций"""
        for task in self.db.get_all_tasks():
            if task.completed or not task.energy_level:
                continue

            if task.energy_level >= 8:  # Высокий уровень энергозатрат
                settings = self.db.get_reminder_settings(task.user_id)
                if settings and not self._is_quiet_hours(datetime.now().strftime("%H:%M"), settings):
                    message = self._message_formats["energy_warning"].format(
                        task_title=task.title,
                        energy_level=task.energy_level,
                        optimal_time=task.optimal_time or "не указано"
                    )
                    await self.bot.send_message(task.user_id, message)

    async def _send_daily_summary(self, user_id: int):
        """Отправка утренней сводки задач с учетом энергозатрат и оптимального времени"""
        try:
            settings = self.db.get_reminder_settings(user_id)
            if not settings or "daily" not in settings.reminder_types:
                return

            if self._is_quiet_hours(datetime.now().strftime("%H:%M"), settings):
                logger.info(f"Пропуск утренней сводки для пользователя {user_id} - тихие часы")
                return

            tasks = self.db.get_upcoming_tasks(user_id)
            if not tasks:
                return

            # Сортировка задач по энергозатратам и приоритету
            tasks.sort(key=lambda x: (
                -(x.energy_level or 0),  # Сначала самые энергозатратные
                self._priority_to_number(x.priority),
                x.due_date
            ))

            message = "🌅 Доброе утро! План на сегодня:\n\n"

            # Группировка по оптимальному времени выполнения
            time_groups = {
                "morning": "🌄 Утренние задачи",
                "afternoon": "☀️ Дневные задачи",
                "evening": "🌙 Вечерние задачи"
            }

            grouped_tasks = {}
            for task in tasks:
                time_group = task.optimal_time or "other"
                if time_group not in grouped_tasks:
                    grouped_tasks[time_group] = []
                grouped_tasks[time_group].append(task)

            for time_group, group_name in time_groups.items():
                if time_group in grouped_tasks:
                    message += f"\n{group_name}:\n"
                    for task in grouped_tasks[time_group]:
                        urgency = self._get_urgency_emoji(task.due_date)
                        energy = "⚡️" * ((task.energy_level or 0) // 2)  # Визуализация энергозатрат
                        message += (
                            f"{urgency} {task.title}\n"
                            f"{energy} Энергозатраты: {task.energy_level or 'не указано'}/10\n"
                            f"⏰ До: {task.due_date.strftime(Config.DATETIME_FORMAT)}\n\n"
                        )

            # Добавляем общие рекомендации
            message += "\n📋 Рекомендации:\n"
            message += "• Начните с самых энергозатратных задач, пока у вас есть силы\n"
            message += "• Делайте перерывы между сложными задачами\n"
            message += "• Группируйте похожие задачи для эффективной работы"

            await self.bot.send_message(user_id, message)

        except Exception as e:
            logger.error(f"Ошибка при отправке утренней сводки: {str(e)}", exc_info=True)

    async def _send_evening_summary(self, user_id: int):
        """Отправка вечерней сводки с анализом дня и рекомендациями"""
        try:
            settings = self.db.get_reminder_settings(user_id)
            if not settings or "daily" not in settings.reminder_types:
                return

            if self._is_quiet_hours(datetime.now().strftime("%H:%M"), settings):
                logger.info(f"Пропуск вечерней сводки для пользователя {user_id} - тихие часы")
                return

            tasks = self.db.get_tasks(user_id)
            if not tasks:
                return

            completed_tasks = [t for t in tasks if t.completed]
            pending_tasks = [t for t in tasks if not t.completed]

            message = "🌙 Подведем итоги дня:\n\n"

            # Анализ выполненных задач
            if completed_tasks:
                total_energy = sum(t.energy_level or 5 for t in completed_tasks)
                message += f"✅ Выполнено задач: {len(completed_tasks)}\n"
                message += f"⚡️ Суммарные энергозатраты: {total_energy}\n\n"
                message += "Завершенные задачи:\n"
                for task in completed_tasks:
                    message += f"• {task.title}\n"
                message += "\n"

            # Анализ предстоящих задач
            if pending_tasks:
                message += "⏳ Предстоящие задачи:\n"
                for task in pending_tasks:
                    due_date = task.due_date.strftime(Config.DATETIME_FORMAT)
                    energy = task.energy_level or 5
                    message += f"• {task.title} (энергия: {energy}/10, до {due_date})\n"

            # Расчет продуктивности и рекомендации
            if tasks:
                completed_energy = sum(t.energy_level or 5 for t in completed_tasks)
                total_energy = sum(t.energy_level or 5 for t in tasks)
                productivity = len(completed_tasks) / len(tasks) * 100
                energy_efficiency = (completed_energy / total_energy * 100) if total_energy > 0 else 0

                message += f"\n📊 Статистика:\n"
                message += f"• Продуктивность: {productivity:.1f}%\n"
                message += f"• Эффективность по энергии: {energy_efficiency:.1f}%\n"

                # Рекомендации на завтра
                message += "\n💡 Рекомендации на завтра:\n"
                if pending_tasks:
                    high_energy_tasks = [t for t in pending_tasks if (t.energy_level or 5) >= 8]
                    if high_energy_tasks:
                        message += "• Запланируйте энергозатратные задачи на утро:\n"
                        for task in high_energy_tasks[:3]:  # Топ-3 энергозатратных задачи
                            message += f"  - {task.title} (⚡️{task.energy_level}/10)\n"

            await self.bot.send_message(user_id, message)

        except Exception as e:
            logger.error(f"Ошибка при отправке вечерней сводки: {str(e)}", exc_info=True)

    async def _check_upcoming_tasks(self, user_id: int, priority: str):
        """Проверка и отправка напоминаний о предстоящих задачах с учетом приоритета и энергозатрат"""
        try:
            settings = self.db.get_reminder_settings(user_id)
            if not settings:
                return

            if self._is_quiet_hours(datetime.now().strftime("%H:%M"), settings):
                return

            now = datetime.now()
            tasks = [t for t in self.db.get_upcoming_tasks(user_id)
                    if t.priority == priority and not t.completed]

            for task in tasks:
                time_until_due = task.due_date - now

                # Настраиваем частоту напоминаний в зависимости от приоритета и настроек
                reminder_interval = timedelta(minutes=getattr(
                    settings,
                    f"priority_{priority.lower()}_interval",
                    self._reminder_intervals[priority]
                ))

                # Увеличиваем частоту напоминаний для срочных задач
                if time_until_due <= timedelta(hours=1):
                    reminder_interval = timedelta(minutes=reminder_interval.total_seconds() // 120)

                if time_until_due <= timedelta(hours=24):
                    message_format = (
                        self._message_formats["urgent_reminder"]
                        if time_until_due <= timedelta(hours=1)
                        else self._message_formats["task_reminder"]
                    )

                    message = message_format.format(
                        task_title=task.title,
                        time_left=self._format_timedelta(time_until_due)
                    )

                    # Добавляем информацию об энергозатратах для важных задач
                    if task.energy_level and task.energy_level >= 7:
                        message += f"\n⚡️ Энергозатратность: {task.energy_level}/10"
                        if task.optimal_time:
                            message += f"\n⏰ Оптимальное время: {task.optimal_time}"

                    await self.bot.send_message(user_id, message)

        except Exception as e:
            logger.error(f"Ошибка при проверке предстоящих задач: {str(e)}", exc_info=True)

    def _is_quiet_hours(self, current_time: str, settings) -> bool:
        """Проверяет, попадает ли текущее время в тихие часы"""
        try:
            current = datetime.strptime(current_time, "%H:%M").time()
            quiet_start = datetime.strptime(settings.quiet_hours_start, "%H:%M").time()
            quiet_end = datetime.strptime(settings.quiet_hours_end, "%H:%M").time()

            if quiet_start <= quiet_end:
                return quiet_start <= current <= quiet_end
            else:  # Если тихие часы переходят через полночь
                return current >= quiet_start or current <= quiet_end

        except ValueError:
            logger.error("Ошибка при проверке тихих часов", exc_info=True)
            return False

    def _priority_to_number(self, priority: str) -> int:
        """Преобразует приоритет в число для сортировки"""
        priority_map = {
            Config.PRIORITY_HIGH: 1,
            Config.PRIORITY_MEDIUM: 2,
            Config.PRIORITY_LOW: 3
        }
        return priority_map.get(priority, 99)

    def _get_urgency_emoji(self, due_date: datetime) -> str:
        """Возвращает эмодзи в зависимости от срочности"""
        time_until = due_date - datetime.now()
        if time_until <= timedelta(hours=1):
            return "🚨"  # Критическая срочность
        elif time_until <= timedelta(hours=3):
            return "⚠️"  # Высокая срочность
        elif time_until <= timedelta(hours=24):
            return "❗️"  # Средняя срочность
        return "ℹ️"     # Низкая срочность

    def _format_timedelta(self, td: timedelta) -> str:
        """Форматирует промежуток времени в читаемый вид"""
        days = td.days
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60

        parts = []
        if days > 0:
            parts.append(f"{days} дн.")
        if hours > 0:
            parts.append(f"{hours} ч.")
        if minutes > 0:
            parts.append(f"{minutes} мин.")

        return " ".join(parts) if parts else "менее минуты"

    def add_task_reminder(self, task_id: int, user_id: int, due_date: datetime):
        """
        Добавление напоминания для конкретной задачи

        :param task_id: ID задачи
        :param user_id: ID пользователя
        :param due_date: Срок выполнения задачи
        """
        settings = self.db.get_reminder_settings(user_id)
        if not settings:
            return

        task = self.db.get_task(task_id)
        if not task:
            return

        # Настраиваем время напоминания с учетом энергозатрат
        advance_time = settings.default_reminder_time
        if task.energy_level and task.energy_level >= 8:
            # Для энергозатратных задач увеличиваем время предварительного напоминания
            advance_time *= 1.5

        reminder_time = due_date - timedelta(minutes=int(advance_time))

        if reminder_time > datetime.now():
            self.scheduler.add_job(
                self._send_task_reminder,
                "date",
                run_date=reminder_time,
                args=[task_id, user_id],
                id=f"task_{task_id}",
                replace_existing=True
            )
            logger.debug(f"Добавлено напоминание для задачи {task_id} на {reminder_time}")

    async def _send_task_reminder(self, task_id: int, user_id: int):
        """
        Отправка напоминания о конкретной задаче

        :param task_id: ID задачи
        :param user_id: ID пользователя
        """
        try:
            settings = self.db.get_reminder_settings(user_id)
            if not settings:
                return

            if self._is_quiet_hours(datetime.now().strftime("%H:%M"), settings):
                return

            task = self.db.get_task(task_id)
            if task and not task.completed:
                time_until = task.due_date - datetime.now()
                message = self._message_formats["task_reminder"].format(
                    task_title=task.title,
                    time_left=self._format_timedelta(time_until)
                )

                # Добавляем информацию об энергозатратах
                if task.energy_level:
                    message += f"\n⚡️ Энергозатратность: {task.energy_level}/10"
                    if task.optimal_time:
                        message += f"\n⌚️ Оптимальное время: {task.optimal_time}"

                await self.bot.send_message(user_id, message)
        except Exception as e:
            logger.error(f"Ошибка при отправке напоминания о задаче: {str(e)}", exc_info=True)
