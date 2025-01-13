"""AI service v2 with improved time structure support"""
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import openai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.database.models_v2 import TimeBlock, Priority, UserPreferences
from src.core.config import Config

logger = logging.getLogger(__name__)

class AIServiceV2:
    """Service for AI-powered plan analysis with time structure"""
    
    def __init__(self):
        """Initialize AI service"""
        self.openai_client = AsyncOpenAI(
            api_key=Config.OPENAI_API_KEY,
            timeout=30.0
        )
        self.cache = {}  # Simple in-memory cache
        self.logger = logging.getLogger(__name__)
        self.logger.info("AI service v2 initialized successfully")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _get_completion(self, messages: List[Dict[str, str]], response_format: Optional[Dict] = None) -> Dict:
        """Get completion from OpenAI with caching and retry"""
        cache_key = str(hash(str(messages)))
        
        if cache_key in self.cache:
            self.logger.info("Cache hit for messages")
            return self.cache[cache_key]

        try:
            params = {
                "model": Config.OPENAI_MODEL,
                "messages": messages,
                "max_tokens": Config.MAX_TOKENS,
                "temperature": 0.7,  # Немного снижаем креативность для более структурированных ответов
            }
            
            if response_format:
                params["response_format"] = response_format

            response = await self.openai_client.chat.completions.create(**params)
            result = json.loads(response.choices[0].message.content)
            
            # Cache the result
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            self.logger.error(f"Error in OpenAI API call: {str(e)}")
            raise

    async def analyze_plan_v2(self, plan_text: str, user_preferences: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze plan text and create structured plan with time blocks"""
        try:
            # Формируем промпт с учетом предпочтений пользователя
            system_message = {
                "role": "system",
                "content": """Ты Рик из "Рика и Морти", помогающий с планированием. Твоя задача - создать структурированный план с четкими временными рамками.

Правила:
1. Юмор ограничен 20% ответа
2. Каждый шаг должен иметь конкретную длительность
3. Приоритеты должны быть реалистичными
4. Общая длительность плана не должна превышать 4 часа

Формат ответа должен быть в JSON:
{
    "title": "Название плана",
    "description": "Описание плана",
    "duration_minutes": 120,
    "priority": "high/medium/low",
    "steps": [
        {
            "title": "Название шага",
            "description": "Описание шага",
            "duration_minutes": 30,
            "priority": "high/medium/low"
        }
    ]
}"""
            }

            user_message = {
                "role": "user",
                "content": f"""План: {plan_text}

Предпочтения пользователя:
{json.dumps(user_preferences, indent=2) if user_preferences else 'Нет предпочтений'}"""
            }

            messages = [system_message, user_message]
            response_format = {"type": "json_object"}
            
            # Получаем структурированный план от AI
            plan_data = await self._get_completion(messages, response_format)
            
            # Валидируем и нормализуем данные
            validated_plan = self._validate_plan_data(plan_data)
            
            return validated_plan
            
        except Exception as e:
            self.logger.error(f"Error in plan analysis: {str(e)}")
            raise

    def _validate_plan_data(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize plan data"""
        try:
            # Проверяем обязательные поля
            required_fields = ['title', 'description', 'duration_minutes', 'priority', 'steps']
            for field in required_fields:
                if field not in plan_data:
                    raise ValueError(f"Missing required field: {field}")

            # Нормализуем приоритет
            plan_data['priority'] = plan_data['priority'].lower()
            if plan_data['priority'] not in ['high', 'medium', 'low']:
                plan_data['priority'] = 'medium'

            # Проверяем длительность
            if not isinstance(plan_data['duration_minutes'], int) or plan_data['duration_minutes'] <= 0:
                raise ValueError("Invalid duration")
            if plan_data['duration_minutes'] > 240:  # 4 часа максимум
                plan_data['duration_minutes'] = 240

            # Валидируем шаги
            total_step_duration = 0
            for step in plan_data['steps']:
                # Проверяем обязательные поля шага
                if not all(k in step for k in ['title', 'duration_minutes']):
                    raise ValueError("Invalid step data")

                # Нормализуем длительность шага
                step['duration_minutes'] = min(int(step['duration_minutes']), 120)
                total_step_duration += step['duration_minutes']

                # Нормализуем приоритет шага
                if 'priority' in step:
                    step['priority'] = step['priority'].lower()
                    if step['priority'] not in ['high', 'medium', 'low']:
                        step['priority'] = 'medium'

            # Проверяем общую длительность шагов
            if total_step_duration > plan_data['duration_minutes']:
                # Пропорционально уменьшаем длительность шагов
                ratio = plan_data['duration_minutes'] / total_step_duration
                for step in plan_data['steps']:
                    step['duration_minutes'] = int(step['duration_minutes'] * ratio)

            return plan_data

        except Exception as e:
            self.logger.error(f"Error in plan validation: {str(e)}")
            raise ValueError("Invalid plan data structure")
