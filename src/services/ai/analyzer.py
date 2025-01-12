"""Task analyzer using OpenAI API"""
import json
import logging
from typing import Optional, Dict
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

    async def analyze_task(self, text: str) -> Optional[Dict]:
        """
        Анализ текста задачи с помощью OpenAI API

        Args:
            text: Текст задачи для анализа

        Returns:
            Dict с результатом анализа или None при ошибке
        """
        try:
            logger.debug(f"Анализ текста: {text[:100]}...")

            deadline = datetime.now() + timedelta(days=1)
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты - планировщик задач. Проанализируй задачу и верни JSON с планом:\n"
                        "{\n"
                        "  'priority': 'high/medium/low',\n"
                        "  'deadline': 'YYYY-MM-DD HH:MM',\n"
                        "  'duration': минуты,\n"
                        "  'subtasks': [\n"
                        "    {\n"
                        "      'title': 'название',\n"
                        "      'duration': минуты\n"
                        "    }\n"
                        "  ]\n"
                        "}"
                    )
                },
                {
                    "role": "user",
                    "content": f"Задача: {text}"
                }
            ]

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            if not response.choices:
                return None

            result = json.loads(response.choices[0].message.content)
            result['deadline'] = deadline.strftime('%Y-%m-%d %H:%M')
            logger.info(f"Анализ выполнен. Результат: {result}")
            return result

        except Exception as e:
            logger.error(f"Ошибка при анализе: {str(e)}", exc_info=True)
            return None