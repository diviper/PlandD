"""Task analyzer using OpenAI API"""
import json
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta

from openai import AsyncOpenAI

from src.core.config import Config

logger = logging.getLogger(__name__)

class TaskAnalyzer:
    """Анализатор задач с использованием OpenAI API"""

    def __init__(self):
        """Initialize TaskAnalyzer with OpenAI client"""
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("TaskAnalyzer инициализирован")

    async def analyze_plan(self, text: str, plan_type: str) -> Optional[Dict]:
        """
        Анализ описания плана с помощью OpenAI API

        Args:
            text: Описание плана/цели
            plan_type: Тип плана (personal/work/study/health)

        Returns:
            Dict с результатом анализа или None при ошибке
        """
        try:
            logger.debug(f"Анализ плана типа {plan_type}: {text[:100]}...")
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты - AI планировщик. Проанализируй цель и создай структурированный план.\n"
                        "Верни JSON в формате:\n"
                        "{\n"
                        "  'title': 'краткое название плана',\n"
                        "  'description': 'описание цели',\n"
                        "  'estimated_duration': 'примерная длительность в днях',\n"
                        "  'priority': 'high/medium/low',\n"
                        "  'steps': [\n"
                        "    {\n"
                        "      'title': 'название шага',\n"
                        "      'description': 'описание',\n"
                        "      'duration': 'длительность в днях',\n"
                        "      'prerequisites': ['id предыдущих шагов'],\n"
                        "      'metrics': ['критерии выполнения']\n"
                        "    }\n"
                        "  ],\n"
                        "  'recommendations': ['советы по выполнению'],\n"
                        "  'potential_blockers': ['возможные препятствия']\n"
                        "}"
                    )
                },
                {
                    "role": "user",
                    "content": f"Тип плана: {plan_type}\nОписание: {text}"
                }
            ]

            response = await self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            result = response.choices[0].message.content
            plan_data = json.loads(result)
            
            logger.info(f"План успешно проанализирован: {plan_data['title']}")
            return plan_data

        except Exception as e:
            logger.error(f"Ошибка при анализе плана: {str(e)}")
            return None

    async def suggest_improvements(self, plan_data: Dict, progress: List[Dict]) -> Optional[Dict]:
        """
        Анализ прогресса и предложение улучшений

        Args:
            plan_data: Текущий план
            progress: История прогресса

        Returns:
            Dict с предложениями по улучшению или None при ошибке
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Проанализируй прогресс выполнения плана и предложи улучшения.\n"
                        "Верни JSON в формате:\n"
                        "{\n"
                        "  'analysis': 'общий анализ прогресса',\n"
                        "  'improvements': ['конкретные предложения'],\n"
                        "  'timeline_adjustment': 'нужно ли скорректировать сроки',\n"
                        "  'priority_changes': ['предложения по изменению приоритетов']\n"
                        "}"
                    )
                },
                {
                    "role": "user",
                    "content": f"План: {json.dumps(plan_data)}\nПрогресс: {json.dumps(progress)}"
                }
            ]

            response = await self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            result = response.choices[0].message.content
            suggestions = json.loads(result)
            
            logger.info("Анализ прогресса выполнен успешно")
            return suggestions

        except Exception as e:
            logger.error(f"Ошибка при анализе прогресса: {str(e)}")
            return None