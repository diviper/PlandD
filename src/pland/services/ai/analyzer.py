"""Task analyzer using OpenAI API"""
import json
import logging
from typing import Optional, Dict, Any
import asyncio

from openai import AsyncOpenAI, APIError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from pland.core.config import Config

logger = logging.getLogger(__name__)

class TaskAnalyzerError(Exception):
    """Base exception for task analyzer errors"""
    pass

class TaskAnalyzer:
    """Анализатор задач с использованием OpenAI API"""

    def __init__(self):
        """Initialize TaskAnalyzer with OpenAI client"""
        if not Config.OPENAI_API_KEY:
            logger.error("OpenAI API key не найден в переменных окружения")
            raise ValueError("OpenAI API key обязателен")

        logger.info("Инициализация TaskAnalyzer...")
        logger.debug(f"Используется OpenAI API ключ оканчивающийся на: ...{Config.OPENAI_API_KEY[-4:]}")

        try:
            self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
            logger.info("TaskAnalyzer успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации TaskAnalyzer: {str(e)}", exc_info=True)
            raise

    async def analyze_task(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Simple task analysis with OpenAI - for testing connection and basic functionality

        Args:
            text: Task description text

        Returns:
            Dictionary with basic task analysis or None if analysis fails
        """
        try:
            logger.info(f"Начало анализа задачи: {text[:100]}...")

            # Simple system message for testing
            messages = [
                {
                    "role": "system",
                    "content": "Ты помощник по анализу задач. Проанализируй задачу кратко."
                },
                {
                    "role": "user", 
                    "content": f"Проанализируй задачу: {text}"
                }
            ]

            try:
                logger.info("Отправка тестового запроса к OpenAI API")
                response = await self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=100,
                    response_format={"type": "json_object"}
                )

                logger.info("Получен ответ от OpenAI API")
                logger.debug(f"Ответ API: {response.choices[0].message.content}")

                result = json.loads(response.choices[0].message.content)
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга ответа API: {str(e)}")
                return None

        except RateLimitError as e:
            logger.error(f"Превышен лимит запросов: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при анализе: {str(e)}", exc_info=True)
            return None

    async def test_api_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            logger.info("Проверка подключения к OpenAI API...")
            messages = [{"role": "user", "content": "Test connection"}]

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=10,
                response_format={"type": "json_object"}
            )

            if response and response.choices:
                logger.info("✓ Тест подключения к OpenAI API успешен")
                return True

            logger.error("Тест подключения к OpenAI API не удался: Пустой ответ")
            return False

        except Exception as e:
            logger.error(f"Ошибка при проверке подключения к API: {str(e)}", exc_info=True)
            return False

from typing import List