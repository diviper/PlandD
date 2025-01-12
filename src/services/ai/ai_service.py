"""AI service for plan analysis and optimization"""
import json
import logging
from typing import Dict, Any, Optional

import openai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.database.database import Database
from src.database.models import UserPreferences

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered plan analysis and optimization"""
    
    def __init__(self, db: Database):
        """Initialize AI service"""
        self.client = AsyncOpenAI()
        self.db = db
        logger.info("AI service initialized successfully")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_plan(self, description: str, plan_type: str) -> Optional[Dict[str, Any]]:
        """Analyze plan description and generate structured plan"""
        try:
            logger.debug(f"Анализ плана типа {plan_type}: {description[:100]}...")
            
            system_prompt = """Ты - AI планировщик. Проанализируй цель и создай структурированный план.
Верни JSON в формате:
{
  'title': 'краткое название плана',
  'description': 'описание цели',
  'estimated_duration': 'примерная длительность в днях',
  'priority': 'high/medium/low',
  'steps': [
    {
      'title': 'название шага',
      'description': 'описание',
      'duration': 'длительность в днях',
      'prerequisites': ['id предыдущих шагов'],
      'metrics': ['критерии выполнения']
    }
  ],
  'recommendations': ['советы по выполнению'],
  'potential_blockers': ['возможные препятствия']
}"""

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Тип плана: {plan_type}\nОписание: {description}"}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            plan_data = json.loads(response.choices[0].message.content.replace("'", '"'))
            logger.info(f"План успешно проанализирован: {plan_data['title']}")
            return plan_data

        except Exception as e:
            logger.error(f"Ошибка при анализе плана: {str(e)}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def learn_patterns(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Learn and analyze user patterns"""
        try:
            session = self.db.get_session()
            try:
                prefs = session.query(UserPreferences).filter_by(user_id=user_id).first()
                if not prefs:
                    raise ValueError(f"User preferences not found for user {user_id}")
                
                # Формируем данные о предпочтениях в JSON
                preferences = {
                    "work_hours": prefs.preferred_work_hours,
                    "peak_hours": prefs.peak_productivity_hours,
                    "energy_curve": prefs.typical_energy_curve,
                    "success_rate": prefs.avg_task_completion_rate,
                    "distractions": prefs.common_distractions
                }
            finally:
                session.close()

            system_prompt = """Проанализируй паттерны пользователя и предложи оптимизации.
Верни JSON в формате:
{
  "productivity_patterns": {
    "peak_hours": ["время максимальной продуктивности"],
    "optimal_duration": "оптимальная длительность задач",
    "break_patterns": "оптимальные перерывы"
  },
  "success_factors": ["факторы успеха"],
  "risk_factors": ["факторы риска"],
  "recommendations": ["рекомендации"]
}"""

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Предпочтения: {json.dumps(preferences)}"}
                ],
                max_tokens=500,
                temperature=0.7
            )

            patterns = json.loads(response.choices[0].message.content)
            logger.info(f"Паттерны пользователя {user_id} проанализированы")
            return patterns

        except Exception as e:
            logger.error(f"Ошибка при анализе паттернов: {str(e)}")
            return None
