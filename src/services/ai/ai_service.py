"""AI service for plan analysis and optimization"""
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import openai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.database.database import Database
from src.database.models import UserPreferences
from src.core.config import Config

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered plan analysis and optimization"""
    
    def __init__(self, db: Database):
        """Initialize AI service"""
        self.db = db
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
