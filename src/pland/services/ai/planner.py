"""Task planner using OpenAI API for advanced planning"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from openai import AsyncOpenAI, APIError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pland.core.config import Config

logger = logging.getLogger(__name__)

class TaskPlanner:
    """Планировщик задач с использованием AI"""

    def __init__(self):
        """Initialize TaskPlanner with OpenAI client"""
        if not Config.OPENAI_API_KEY:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("TaskPlanner initialized successfully")

    async def optimize_schedule(
        self, 
        tasks: List[Dict], 
        user_schedule: Optional[Dict] = None,
        energy_level: Optional[int] = None
    ) -> Tuple[List[Dict], List[str]]:
        """
        Оптимизирует расписание задач с учетом приоритетов, энергии и конфликтов

        Args:
            tasks: Список задач для оптимизации
            user_schedule: График пользователя (необязательно)
            energy_level: Текущий уровень энергии пользователя (1-10)

        Returns:
            Tuple[List[Dict], List[str]]: (оптимизированный список задач, предупреждения)
        """
        try:
            logger.debug(f"Starting schedule optimization for {len(tasks)} tasks")
            logger.debug(f"User schedule: {user_schedule}")
            logger.debug(f"Energy level: {energy_level}")

            system_prompt = {
                "role": "system",
                "content": (
                    "Ты - эксперт по оптимизации расписания и тайм-менеджменту. "
                    "Проанализируй список задач и создай оптимальное расписание с учетом:\n"
                    "1. Приоритетов, дедлайнов и зависимостей между задачами\n"
                    "2. Возможностей параллельного выполнения\n"
                    "3. Энергетического состояния пользователя\n"
                    "4. Оптимального времени суток для каждой задачи\n"
                    "5. Необходимых перерывов между задачами\n\n"
                    "Верни результат в формате JSON:\n"
                    "{\n"
                    "  'optimized_tasks': [\n"
                    "    {\n"
                    "      'id': число,\n"
                    "      'start_time': 'YYYY-MM-DD HH:mm',\n"
                    "      'estimated_energy_cost': число (1-10),\n"
                    "      'recommended_breaks': [{'duration': минуты, 'after_task': id}],\n"
                    "      'parallel_with': [id] или null,\n"
                    "      'optimization_applied': ['примененные_оптимизации']\n"
                    "    }\n"
                    "  ],\n"
                    "  'warnings': ['описание конфликтов или проблем'],\n"
                    "  'energy_management': {\n"
                    "    'morning_tasks': [id],\n"
                    "    'afternoon_tasks': [id],\n"
                    "    'evening_tasks': [id]\n"
                    "  },\n"
                    "  'schedule_efficiency': {\n"
                    "    'total_duration': минуты,\n"
                    "    'parallel_tasks_saved': минуты,\n"
                    "    'optimization_saved': минуты\n"
                    "  }\n"
                    "}"
                )
            }

            # Подготовка контекста для API
            tasks_info = []
            for task in tasks:
                task_info = {
                    "id": task.get("id"),
                    "title": task.get("title"),
                    "priority": task.get("priority"),
                    "duration": task.get("estimated_duration", 30),
                    "due_date": task.get("due_date").strftime(Config.DATETIME_FORMAT),
                    "energy_level": task.get("energy_level", 5),
                    "dependencies": task.get("dependencies", []),
                    "parallel_possible": task.get("parallel_possible", False),
                    "best_time_of_day": task.get("best_time_of_day", "morning"),
                    "optimization_suggestions": task.get("optimization_suggestions", [])
                }
                tasks_info.append(task_info)

            logger.debug(f"Prepared tasks info for API: {tasks_info}")

            context_message = {
                "role": "user",
                "content": (
                    f"Оптимизируй расписание для следующих задач:\n"
                    f"{json.dumps(tasks_info, ensure_ascii=False, indent=2)}\n"
                    f"Текущий уровень энергии пользователя: {energy_level or 'неизвестен'}"
                )
            }

            if user_schedule:
                context_message["content"] += (
                    f"\nГрафик пользователя: "
                    f"{json.dumps(user_schedule, ensure_ascii=False, indent=2)}"
                )

            response = await self._make_api_request(
                messages=[system_prompt, context_message],
                max_retries=3
            )

            result = json.loads(response.choices[0].message.content)
            logger.debug(f"Received API response: {result}")

            optimized_schedule = result.get("optimized_tasks", [])
            warnings = result.get("warnings", [])
            efficiency_stats = result.get("schedule_efficiency", {})

            # Применяем оптимизацию к исходным задачам
            optimized_tasks = []
            for task in tasks:
                optimization = next(
                    (opt for opt in optimized_schedule if opt["id"] == task.get("id")),
                    None
                )
                if optimization:
                    task.update({
                        "start_time": datetime.strptime(
                            optimization["start_time"],
                            Config.DATETIME_FORMAT
                        ),
                        "energy_cost": optimization["estimated_energy_cost"],
                        "recommended_breaks": optimization["recommended_breaks"],
                        "parallel_with": optimization.get("parallel_with"),
                        "optimization_applied": optimization.get("optimization_applied", [])
                    })
                optimized_tasks.append(task)

            # Добавляем информацию об эффективности расписания в предупреждения
            if efficiency_stats:
                efficiency_msg = (
                    f"Оптимизация сохранила {efficiency_stats.get('optimization_saved', 0)} минут. "
                    f"Параллельное выполнение сэкономило {efficiency_stats.get('parallel_tasks_saved', 0)} минут."
                )
                warnings.append(efficiency_msg)
                logger.info(efficiency_msg)

            logger.info(f"Schedule optimization completed. Found {len(warnings)} potential issues")
            return optimized_tasks, warnings

        except Exception as e:
            error_msg = f"Ошибка при оптимизации расписания: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return tasks, ["Произошла ошибка при оптимизации расписания"]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(APIError)
    )
    async def _make_api_request(self, messages: List[Dict], max_retries: int = 3):
        """Выполняет запрос к API с повторными попытками"""
        try:
            logger.debug("Making API request to OpenAI")
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=Config.TASK_ANALYSIS_SETTINGS["ai_temperature"]
            )
            logger.debug("API request successful")
            return response
        except Exception as e:
            logger.error(f"API request failed: {str(e)}", exc_info=True)
            raise

    def _calculate_energy_distribution(
        self,
        tasks: List[Dict],
        current_energy: int
    ) -> Dict[str, List[int]]:
        """
        Распределяет задачи по времени суток с учетом энергии

        Args:
            tasks: Список задач
            current_energy: Текущий уровень энергии пользователя

        Returns:
            Dict с распределением задач по времени суток
        """
        logger.debug(f"Calculating energy distribution for {len(tasks)} tasks")
        logger.debug(f"Current energy level: {current_energy}")

        morning_tasks = []
        afternoon_tasks = []
        evening_tasks = []

        for task in sorted(tasks, key=lambda x: x.get("energy_level", 5), reverse=True):
            task_id = task.get("id")
            energy_level = task.get("energy_level", 5)
            best_time = task.get("best_time_of_day", "morning")

            # Учитываем предпочтительное время и энергозатратность
            if best_time == "morning" and current_energy >= 7:
                morning_tasks.append(task_id)
            elif best_time == "afternoon" or (4 <= energy_level <= 6):
                afternoon_tasks.append(task_id)
            else:
                evening_tasks.append(task_id)

        result = {
            "morning_tasks": morning_tasks,
            "afternoon_tasks": afternoon_tasks,
            "evening_tasks": evening_tasks
        }
        logger.debug(f"Energy distribution result: {result}")
        return result