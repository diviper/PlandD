"""AI learning service for analyzing user patterns and adapting planning"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from sqlalchemy import func
from openai import AsyncOpenAI

from src.core.config import Config
from src.database.database import Database
from src.database.models import Task, UserPreferences

logger = logging.getLogger(__name__)

class UserPatternLearner:
    """Анализатор паттернов пользователя для адаптивного планирования"""

    def __init__(self, db: Database):
        """Initialize learner with database connection"""
        self.db = db
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("UserPatternLearner initialized")

    async def analyze_user_patterns(self, user_id: int) -> Dict:
        """
        Анализирует паттерны пользователя на основе истории задач

        Args:
            user_id: ID пользователя для анализа

        Returns:
            Dict с обновленными предпочтениями и рекомендациями
        """
        try:
            # Получаем историю задач пользователя
            tasks = await self.db.get_completed_tasks(user_id)
            if not tasks:
                logger.info(f"No completed tasks found for user {user_id}")
                return {}

            # Собираем данные для анализа
            task_data = self._prepare_task_data(tasks)
            
            # Анализируем через AI
            analysis = await self._analyze_with_ai(task_data)
            
            # Обновляем предпочтения пользователя
            await self._update_user_preferences(user_id, analysis)
            
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing user patterns: {str(e)}", exc_info=True)
            return {}

    def _prepare_task_data(self, tasks: List[Task]) -> Dict:
        """Подготавливает данные задач для анализа"""
        task_data = {
            "completion_times": {},  # время завершения по типам задач
            "effectiveness": {},     # эффективность по времени суток
            "duration_accuracy": [], # точность оценки длительности
            "energy_patterns": {},   # паттерны энергии
            "success_rates": {},     # успешность по типам задач
        }

        for task in tasks:
            if not task.completion_time:
                continue

            hour = task.completion_time.hour
            time_of_day = self._get_time_of_day(hour)
            
            # Анализ времени завершения
            task_type = self._categorize_task(task.text)
            if task_type not in task_data["completion_times"]:
                task_data["completion_times"][task_type] = []
            task_data["completion_times"][task_type].append(hour)

            # Анализ эффективности
            if time_of_day not in task_data["effectiveness"]:
                task_data["effectiveness"][time_of_day] = []
            task_data["effectiveness"][time_of_day].append(task.effectiveness or 5)

            # Анализ точности оценки длительности
            if task.actual_duration:
                accuracy = task.actual_duration / task.duration
                task_data["duration_accuracy"].append(accuracy)

            # Анализ энергии
            if task.energy_level:
                if time_of_day not in task_data["energy_patterns"]:
                    task_data["energy_patterns"][time_of_day] = []
                task_data["energy_patterns"][time_of_day].append(task.energy_level)

            # Анализ успешности
            if task_type not in task_data["success_rates"]:
                task_data["success_rates"][task_type] = {"success": 0, "total": 0}
            task_data["success_rates"][task_type]["total"] += 1
            if task.effectiveness and task.effectiveness >= 7:
                task_data["success_rates"][task_type]["success"] += 1

        return task_data

    async def _analyze_with_ai(self, task_data: Dict) -> Dict:
        """Анализирует данные с помощью AI"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты - эксперт по анализу продуктивности и рабочих привычек. "
                        "Проанализируй данные о выполнении задач и создай рекомендации "
                        "по оптимизации планирования."
                    )
                },
                {
                    "role": "user",
                    "content": f"Проанализируй следующие данные о выполнении задач:\n{json.dumps(task_data, indent=2)}"
                }
            ]

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            analysis = json.loads(response.choices[0].message.content)
            logger.info("AI analysis completed successfully")
            return analysis

        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}", exc_info=True)
            return {}

    async def _update_user_preferences(self, user_id: int, analysis: Dict):
        """Обновляет предпочтения пользователя на основе анализа"""
        try:
            session = self.db.get_session()
            prefs = session.query(UserPreferences).filter_by(user_id=user_id).first()
            
            if not prefs:
                prefs = UserPreferences(user_id=user_id)
                session.add(prefs)

            # Обновляем предпочтения на основе анализа
            if "preferred_hours" in analysis:
                prefs.preferred_work_hours = analysis["preferred_hours"]
            
            if "peak_hours" in analysis:
                prefs.peak_productivity_hours = analysis["peak_hours"]
            
            if "energy_curve" in analysis:
                prefs.typical_energy_curve = analysis["energy_curve"]
            
            if "success_patterns" in analysis:
                prefs.task_success_patterns = analysis["success_patterns"]
            
            if "productivity_factors" in analysis:
                prefs.productivity_factors = analysis["productivity_factors"]

            # Увеличиваем уверенность в данных
            prefs.confidence_score = min(1.0, (prefs.confidence_score or 0.5) + 0.1)
            prefs.last_analysis = datetime.utcnow()

            session.commit()
            logger.info(f"Updated preferences for user {user_id}")

        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}", exc_info=True)
            session.rollback()
        finally:
            session.close()

    def _get_time_of_day(self, hour: int) -> str:
        """Определяет время суток по часу"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"

    def _categorize_task(self, text: str) -> str:
        """Простая категоризация задачи по тексту"""
        text = text.lower()
        if any(word in text for word in ["встреча", "созвон", "meeting", "call"]):
            return "meeting"
        elif any(word in text for word in ["код", "программ", "code", "program"]):
            return "coding"
        elif any(word in text for word in ["документ", "отчет", "document", "report"]):
            return "documentation"
        elif any(word in text for word in ["почта", "email", "письм"]):
            return "email"
        else:
            return "other"
