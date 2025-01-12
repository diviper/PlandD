"""AI service for plan analysis and optimization"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

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
    async def analyze_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Анализ текста для извлечения структурированной информации"""
        try:
            system_prompt = """Ты - ИИ помощник в стиле Рика из "Рика и Морти". 
Проанализируй текст и верни структурированную информацию.
Используй научный подход с щепоткой безумного юмора.

Верни JSON в формате:
{
    'task_type': 'тип задачи (work/personal/adventure)',
    'priority': 'high/medium/low',
    'estimated_duration': 'длительность в минутах (int)',
    'complexity': 'сложность 1-10',
    'rick_comment': 'саркастичный комментарий от Рика',
    'parsed_date': 'если есть дата в тексте, в формате YYYY-MM-DD',
    'parsed_time': 'если есть время в тексте, в формате HH:MM',
    'entities': {
        'people': ['упомянутые люди'],
        'places': ['упомянутые места'],
        'items': ['упомянутые предметы']
    }
}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Текст: {text}"}
            ]

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )

            result = json.loads(response.choices[0].message.content.replace("'", '"'))
            logger.debug(f"Результат анализа текста: {result}")
            return result

        except Exception as e:
            logger.error(f"Ошибка при анализе текста: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_plan(self, description: str, plan_type: str = "task") -> Optional[Dict[str, Any]]:
        """Analyze plan description and generate structured plan"""
        try:
            logger.debug(f"Анализ плана типа {plan_type}: {description[:100]}...")
            
            system_prompt = """Ты - ИИ помощник в стиле Рика из "Рика и Морти". 
Проанализируй план и разбей его на конкретные шаги. Используй научный подход с щепоткой безумного юмора.

Верни JSON в формате:
{
    'title': 'краткое название плана в стиле Рика',
    'steps': [
        {
            'description': 'описание шага с отсылкой к шоу',
            'duration': 'длительность в минутах (int)',
            'priority': 'high/medium/low',
            'rick_comment': 'саркастичный комментарий от Рика'
        }
    ],
    'suggestions': 'общие рекомендации в стиле Рика',
    'energy_required': 'high/medium/low',
    'dimension_risk': 'шуточная оценка риска для мультивселенной'
}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"План: {description}"}
            ]

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.8,
                max_tokens=1000
            )

            result = json.loads(response.choices[0].message.content.replace("'", '"'))
            logger.debug(f"Результат анализа плана: {result}")
            return result

        except Exception as e:
            logger.error(f"Ошибка при анализе плана: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(self, context: Dict[str, Any]) -> str:
        """Генерация ответа в стиле Рика"""
        try:
            prompt = f"""На основе этих данных создай ответ в стиле Рика из "Рика и Морти":
            {json.dumps(context, ensure_ascii=False, indent=2)}
            
            Добавь научное безумие и сарказм!"""

            messages = [
                {"role": "system", "content": "Ты - Рик Санчез, гений и безумный ученый."},
                {"role": "user", "content": prompt}
            ]

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.8,
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            return "Упс, что-то пошло не так... *burp*"

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
            logger.error(f"Ошибка при анализе паттернов: {e}")
            return None
