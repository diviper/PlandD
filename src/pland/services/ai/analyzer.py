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
        Анализ текста задачи с помощью OpenAI API

        Args:
            text: Текст задачи для анализа

        Returns:
            Dict с результатом анализа или None при ошибке
        """
        try:
            logger.debug(f"Начинаю анализ текста: {text[:100]}...")

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты - эксперт по анализу задач. Проанализируй задачу и верни результат в JSON формате:\n"
                        "{\n"
                        "  'priority': 'высокий/средний/низкий',\n"
                        "  'estimated_time': 'предполагаемое время в минутах',\n"
                        "  'complexity': 'легкая/средняя/сложная',\n"
                        "  'energy_level': число от 1 до 10,\n"
                        "  'subtasks': ['подзадача1', 'подзадача2', ...],\n"
                        "  'recommendations': ['рекомендация1', 'рекомендация2', ...]\n"
                        "}"
                    )
                },
                {
                    "role": "user",
                    "content": f"Проанализируй задачу: {text}"
                }
            ]

            logger.debug("Отправляю запрос к OpenAI API...")
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            logger.debug(f"Получен ответ от API: {response}")

            if not response.choices:
                logger.error("API вернул пустой ответ")
                return None

            result = json.loads(response.choices[0].message.content)
            logger.info(f"Анализ выполнен успешно. Результат: {result}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при разборе JSON ответа: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Ошибка при анализе: {str(e)}", exc_info=True)
            return None

    async def test_api_connection(self) -> bool:
        """Проверка подключения к OpenAI API"""
        try:
            logger.debug("Проверка подключения к OpenAI API...")
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

            success = bool(response and response.choices)
            logger.info(f"Проверка подключения к API {'успешна' if success else 'не удалась'}")
            return success

        except Exception as e:
            logger.error(f"Ошибка при проверке API: {str(e)}", exc_info=True)
            return False