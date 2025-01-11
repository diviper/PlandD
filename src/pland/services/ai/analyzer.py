"""Task analyzer using OpenAI API"""
import json
import logging
from typing import Optional, Dict

from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pland.core.config import Config

logger = logging.getLogger(__name__)

class TaskAnalyzer:
    """Анализатор задач с использованием OpenAI API"""

    def __init__(self):
        """Initialize TaskAnalyzer with OpenAI client"""
        if not Config.OPENAI_API_KEY:
            logger.error("OpenAI API key не найден")
            raise ValueError("OpenAI API key обязателен")

        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("TaskAnalyzer инициализирован")

    async def analyze_task(self, text: str) -> Optional[Dict]:
        """
        Простой анализ текста для проверки работы API

        Args:
            text: Текст для анализа

        Returns:
            Dict с результатом анализа или None при ошибке
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Ты помощник по анализу задач. Проанализируй задачу и верни результат в JSON формате."
                },
                {
                    "role": "user",
                    "content": f"Проанализируй задачу: {text}"
                }
            ]

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            logger.info("Анализ выполнен успешно")
            return result

        except Exception as e:
            logger.error(f"Ошибка при анализе: {str(e)}", exc_info=True)
            return None

    async def test_api_connection(self) -> bool:
        """Проверка подключения к OpenAI API"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": "Тестовое сообщение"
                }
            ]

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=10,
                response_format={"type": "json_object"}
            )

            return bool(response and response.choices)

        except Exception as e:
            logger.error(f"Ошибка при проверке API: {str(e)}", exc_info=True)
            return False