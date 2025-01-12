"""AI service for plan analysis and optimization"""
import json
import logging
import os
from typing import Dict, Any, Optional
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
        # Проверяем наличие API ключа
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not set!")
            
        # Инициализируем клиент
        self.client = AsyncOpenAI(
            api_key=Config.OPENAI_API_KEY,
            timeout=30.0
        )
        self.db = db
        logger.info("AI service initialized successfully")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Анализ текста для извлечения структурированной информации"""
        try:
            logger.info(f"Начинаем анализ текста: {text[:50]}...")
            
            system_prompt = """Ты - ИИ помощник в стиле Рика из "Рика и Морти". 
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

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Текст: {text}"}
            ]

            logger.debug(f"Отправляем запрос к OpenAI API с сообщениями: {messages}")
            
            response = await self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
                response_format={"type": "json_object"}
            )

            logger.debug(f"Получен ответ от OpenAI API: {response}")
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Результат анализа текста: {result}")
            return result

        except Exception as e:
            logger.error(f"Ошибка при анализе текста: {str(e)}")
            logger.exception(e)
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_plan(self, description: str, plan_type: str = "task") -> Optional[Dict[str, Any]]:
        """Analyze plan description and generate structured plan"""
        try:
            logger.info(f"Начинаем анализ плана типа {plan_type}: {description[:50]}...")
            
            system_prompt = """Ты - ИИ помощник в стиле Рика из "Рика и Морти". 
Проанализируй план и разбей его на конкретные шаги. Используй научный подход с щепоткой безумного юмора.

Верни JSON в формате:
{
    "title": "краткое название плана в стиле Рика",
    "steps": [
        {
            "description": "описание шага с отсылкой к шоу",
            "duration": "длительность в минутах (int)",
            "priority": "high/medium/low",
            "rick_comment": "саркастичный комментарий от Рика"
        }
    ],
    "suggestions": "общие рекомендации в стиле Рика",
    "energy_required": "high/medium/low",
    "dimension_risk": "шуточная оценка риска для мультивселенной"
}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"План: {description}"}
            ]

            logger.debug(f"Отправляем запрос к OpenAI API с сообщениями: {messages}")
            
            response = await self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
                response_format={"type": "json_object"}
            )

            logger.debug(f"Получен ответ от OpenAI API: {response}")
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Результат анализа плана: {result}")
            return result

        except Exception as e:
            logger.error(f"Ошибка при анализе плана: {str(e)}")
            logger.exception(e)
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_response(self, context: Dict[str, Any]) -> str:
        """Генерация ответа в стиле Рика"""
        try:
            logger.info("Начинаем генерацию ответа...")
            
            system_prompt = """Ты - ИИ помощник в стиле Рика из "Рика и Морти".
Сгенерируй остроумный ответ на основе предоставленного контекста.
Используй много отсылок к шоу, научных терминов и типичных фраз Рика (*burp*, Морти и т.д.)"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Контекст: {json.dumps(context, ensure_ascii=False)}"}
            ]

            logger.debug(f"Отправляем запрос к OpenAI API с сообщениями: {messages}")
            
            response = await self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )

            logger.debug(f"Получен ответ от OpenAI API: {response}")
            
            result = response.choices[0].message.content
            logger.info(f"Сгенерирован ответ: {result[:100]}...")
            return result

        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {str(e)}")
            logger.exception(e)
            return "Уупс, Морти! *burp* Произошла какая-то квантовая аномалия!"

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
