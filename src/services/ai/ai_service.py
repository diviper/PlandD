"""AI service for plan analysis and optimization"""
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

import openai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.database.database import Database
from src.database.models import UserPreferences
from src.core.config import Config
from src.database.models_v2 import Plan, User, UserPreferences, TimeBlock, Priority
from src.core.exceptions import AIServiceError, InvalidTimeBlockError, InvalidPriorityError

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered plan analysis and optimization"""
    
    def __init__(self, session: AsyncSession):
        """Initialize AI service"""
        self.session = session
        self.openai_client = AsyncOpenAI(
            api_key=Config.OPENAI_API_KEY,
            timeout=30.0
        )
        self.cache = {}  # Simple in-memory cache
        self.logger = logging.getLogger(__name__)
        self.logger.info("AI service initialized successfully")

    async def _get_completion(self, messages: List[Dict[str, str]], response_format: Optional[Dict] = None) -> Dict:
        """Get completion from OpenAI with caching"""
        # Create cache key from messages
        cache_key = str(hash(str(messages)))
        
        # Check cache first
        if cache_key in self.cache:
            self.logger.info("Cache hit for messages")
            return self.cache[cache_key]

        try:
            params = {
                "model": Config.OPENAI_MODEL,
                "messages": messages,
                "max_tokens": Config.MAX_TOKENS,
                "temperature": Config.TEMPERATURE,
            }
            
            if response_format:
                params["response_format"] = response_format

            self.logger.debug(f"Отправляем запрос к OpenAI API с сообщениями: {messages}")
            
            response = await self.openai_client.chat.completions.create(**params)
            
            self.logger.debug(f"Получен ответ от OpenAI API: {response}")
            
            result = json.loads(response.choices[0].message.content) if response_format else response.choices[0].message.content
            
            # Cache the result
            self.cache[cache_key] = result
            
            return result

        except Exception as e:
            self.logger.error(f"Ошибка при запросе к OpenAI API: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Анализ текста для извлечения структурированной информации"""
        self.logger.info(f"Начинаем анализ текста: {text[:50]}...")
        
        messages = [
            {
                "role": "system",
                "content": """Ты - ИИ помощник в стиле Рика из "Рика и Морти". 
Проанализируй текст и верни структурированную информацию.
Используй научный подход с щепоткой безумного юмора.

Верни JSON в формате:
{
    "task_type": "тип задачи (work/personal/adventure)",
    "priority": "high/medium/low",
    "estimated_duration": "длительность в минутах (int)",
    "complexity": "сложность 1-10",
    "rick_comment": "саркастичный комментарий от Рика",
    "parsed_date": "если есть дата в тексте, в формате YYYY-MM-DD",
    "parsed_time": "если есть время в тексте, в формате HH:MM",
    "entities": {
        "people": ["упомянутые люди"],
        "places": ["упомянутые места"],
        "items": ["упомянутые предметы"]
    }
}"""
            },
            {"role": "user", "content": f"Текст: {text}"}
        ]

        result = await self._get_completion(messages, {"type": "json_object"})
        self.logger.info(f"Результат анализа текста: {result}")
        return result

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_plan(self, description: str, plan_type: str = "task") -> Optional[Dict[str, Any]]:
        """Analyze plan description and generate structured plan"""
        self.logger.info(f"Начинаем анализ плана типа {plan_type}: {description[:50]}...")
        
        messages = [
            {
                "role": "system",
                "content": """Ты - ИИ помощник в стиле Рика из "Рика и Морти". 
Проанализируй план и разбей его на конкретные, выполнимые шаги. 
Используй научный подход с щепоткой безумного юмора в стиле Рика.

Правила:
1. Каждый шаг должен быть конкретным и выполнимым действием
2. Длительность должна быть реалистичной
3. Приоритеты должны быть логичными
4. Юмор должен быть уместным и в стиле шоу

Верни JSON в формате:
{
    "title": "краткое название плана (макс 50 символов)",
    "steps": [
        {
            "description": "конкретное действие (макс 100 символов)",
            "duration": "число минут (от 5 до 120)",
            "priority": "high/medium/low",
            "rick_comment": "короткий комментарий от Рика (макс 50 символов)"
        }
    ],
    "suggestions": "2-3 конкретные рекомендации по улучшению плана",
    "energy_required": "high/medium/low",
    "dimension_risk": "шуточная оценка риска (1 предложение)"
}"""
            },
            {"role": "user", "content": f"План: {description}"}
        ]

        result = await self._get_completion(messages, {"type": "json_object"})
        self.logger.info(f"Результат анализа плана: {result}")
        return result

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(self, context: Dict[str, Any]) -> str:
        """Генерация ответа в стиле Рика"""
        self.logger.info("Начинаем генерацию ответа...")
        
        messages = [
            {
                "role": "system",
                "content": """Ты - ИИ помощник в стиле Рика из "Рика и Морти".
Сгенерируй остроумный ответ на основе предоставленного контекста.
Используй много отсылок к шоу, научных терминов и типичных фраз Рика (*burp*, Морти и т.д.)"""
            },
            {"role": "user", "content": f"Контекст: {json.dumps(context, ensure_ascii=False)}"}
        ]

        result = await self._get_completion(messages)
        self.logger.info(f"Сгенерирован ответ: {result[:100]}...")
        return result

    async def learn_patterns(self, user_id: int) -> Dict[str, Any]:
        """Learn and analyze user patterns"""
        try:
            # Получаем историю планов пользователя
            plans = await self.db.get_user_plans(user_id)
            
            if not plans:
                return {
                    "message": "Недостаточно данных для анализа паттернов",
                    "patterns": []
                }

            # Анализируем паттерны
            patterns = []
            total_plans = len(plans)
            completed_plans = len([p for p in plans if p.status == 'completed'])
            
            completion_rate = (completed_plans / total_plans) * 100 if total_plans > 0 else 0
            
            return {
                "message": f"Проанализировано {total_plans} планов",
                "completion_rate": completion_rate,
                "patterns": patterns
            }

        except Exception as e:
            logger.error(f"Ошибка при анализе паттернов: {str(e)}")
            logger.exception(e)
            return {
                "message": "Ошибка при анализе паттернов",
                "patterns": []
            }

    async def analyze_plan_text(self, text: str) -> Dict[str, Any]:
        """Analyze plan text and extract structured information"""
        try:
            if not text:
                raise AIServiceError("Plan text cannot be empty")
                
            # Здесь будет интеграция с OpenAI
            # Пока возвращаем тестовые данные
            return {
                "title": "Test Plan",
                "description": text,
                "time_block": "MORNING",
                "duration_minutes": 60,
                "priority": "MEDIUM",
                "steps": [
                    {
                        "title": "Step 1",
                        "description": "First step",
                        "duration_minutes": 30,
                        "order": 1
                    }
                ]
            }
        except Exception as e:
            raise AIServiceError(f"Failed to analyze plan text: {str(e)}")

    async def suggest_time_block(self, user_id: int, plan_data: Dict[str, Any]) -> TimeBlock:
        """Suggest time block based on user preferences and plan data"""
        try:
            prefs = await self._get_user_preferences(user_id)
            if not prefs or not prefs.work_hours:
                return TimeBlock.MORNING

            work_hours = json.loads(prefs.work_hours)
            start_hour = int(work_hours["start"].split(":")[0])
            
            if 6 <= start_hour < 12:
                return TimeBlock.MORNING
            elif 12 <= start_hour < 18:
                return TimeBlock.AFTERNOON
            elif 18 <= start_hour < 23:
                return TimeBlock.EVENING
            else:
                raise InvalidTimeBlockError("Invalid work hours")
        except Exception as e:
            raise AIServiceError(f"Failed to suggest time block: {str(e)}")

    async def suggest_priority(self, user_id: int, plan_data: Dict[str, Any]) -> Priority:
        """Suggest priority based on plan content and user history"""
        try:
            # Здесь будет интеграция с OpenAI
            # Пока возвращаем тестовые данные
            return Priority.MEDIUM
        except Exception as e:
            raise AIServiceError(f"Failed to suggest priority: {str(e)}")

    async def suggest_steps(self, plan_text: str) -> List[Dict[str, Any]]:
        """Suggest plan steps based on plan description"""
        try:
            if not plan_text:
                raise AIServiceError("Plan text cannot be empty")
                
            # Здесь будет интеграция с OpenAI
            # Пока возвращаем тестовые данные
            return [
                {
                    "title": "Step 1",
                    "description": "First step of the plan",
                    "duration_minutes": 30,
                    "order": 1
                },
                {
                    "title": "Step 2",
                    "description": "Second step of the plan",
                    "duration_minutes": 30,
                    "order": 2
                }
            ]
        except Exception as e:
            raise AIServiceError(f"Failed to suggest steps: {str(e)}")

    async def get_daily_summary(self, user_id: int, date: datetime) -> str:
        """Generate daily summary of user's plans"""
        try:
            # Получаем планы пользователя за день
            stmt = select(Plan).where(
                Plan.user_id == user_id,
                Plan.created_at >= date.replace(hour=0, minute=0),
                Plan.created_at < date.replace(hour=23, minute=59)
            )
            result = await self.session.execute(stmt)
            plans = list(result.scalars().all())

            # Здесь будет интеграция с OpenAI
            # Пока возвращаем простой текстовый отчет
            if not plans:
                return "No plans for today."

            summary = ["Daily Summary:"]
            for plan in plans:
                summary.append(f"- {plan.title} ({plan.time_block.value}, {plan.priority.value})")
            
            return "\n".join(summary)
        except Exception as e:
            raise AIServiceError(f"Failed to generate daily summary: {str(e)}")

    async def get_weekly_analysis(self, user_id: int, start_date: datetime) -> Dict[str, Any]:
        """Generate weekly analysis of user's planning patterns"""
        try:
            # Получаем планы пользователя за неделю
            end_date = start_date.replace(hour=23, minute=59)
            stmt = select(Plan).where(
                Plan.user_id == user_id,
                Plan.created_at >= start_date,
                Plan.created_at <= end_date
            )
            result = await self.session.execute(stmt)
            plans = list(result.scalars().all())

            # Здесь будет интеграция с OpenAI
            # Пока возвращаем базовую статистику
            time_blocks = {tb.value: 0 for tb in TimeBlock}
            priorities = {p.value: 0 for p in Priority}
            total_duration = 0

            for plan in plans:
                time_blocks[plan.time_block.value] += 1
                priorities[plan.priority.value] += 1
                total_duration += plan.duration_minutes

            return {
                "total_plans": len(plans),
                "time_blocks": time_blocks,
                "priorities": priorities,
                "total_duration": total_duration,
                "average_duration": total_duration / len(plans) if plans else 0
            }
        except Exception as e:
            raise AIServiceError(f"Failed to generate weekly analysis: {str(e)}")

    async def _get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences"""
        stmt = select(UserPreferences).where(UserPreferences.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
