"""Task analyzer using OpenAI API"""
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
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
            self._cache = {}
            self._last_request_time = datetime.min
            logger.info("TaskAnalyzer успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации TaskAnalyzer: {str(e)}", exc_info=True)
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError))
    )
    async def analyze_task(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze task text and return structured result with priority, schedule and resources.

        Args:
            text: Task description text

        Returns:
            Dictionary containing analyzed task details or None if analysis fails

        Example response:
        {
            "priority": {
                "level": "high/medium/low",
                "reason": "Explanation of priority",
                "urgency": "urgent/not urgent"
            },
            "schedule": {
                "optimal_time": "morning/afternoon/evening",
                "estimated_duration": "minutes",
                "deadline": "YYYY-MM-DD HH:MM",
                "subtasks": [
                    {
                        "title": "Subtask name",
                        "duration": "minutes",
                        "order": "sequence number"
                    }
                ]
            },
            "resources": {
                "energy_required": 1-10,
                "focus_level": "high/medium/low",
                "materials": ["resource1", "resource2"],
                "prerequisites": ["prerequisite tasks"],
                "dependencies": ["dependent tasks"]
            }
        }
        """
        try:
            logger.info(f"Начало анализа задачи: {text[:100]}...")

            # Check cache
            if text in self._cache:
                logger.info("Найден результат в кэше")
                return self._cache[text]

            # Apply rate limiting
            now = datetime.now()
            time_since_last_request = (now - self._last_request_time).total_seconds()
            if time_since_last_request < 1.0:
                delay = 1.0 - time_since_last_request
                logger.debug(f"Применяется задержка: {delay} секунд")
                await asyncio.sleep(delay)

            messages = [
                {
                    "role": "system",
                    "content": """Ты опытный планировщик задач с глубоким пониманием тайм-менеджмента. 
                    Проанализируй задачу и создай оптимальный план ее выполнения.

                    При анализе учитывай:
                    1. Срочность и важность задачи (матрица Эйзенхауэра)
                    2. Оптимальное время выполнения с учетом биоритмов
                    3. Декомпозицию на подзадачи
                    4. Энергозатраты и необходимый уровень концентрации
                    5. Зависимости и предварительные условия
                    6. Потенциальные риски и препятствия
                    7. Оптимальную последовательность действий

                    Формат ответа JSON:
                    {
                      "priority": {
                        "level": "high/medium/low",
                        "reason": "развернутое объяснение приоритета",
                        "urgency": "срочно/не срочно",
                        "importance": "важно/не важно"
                      },
                      "schedule": {
                        "optimal_time": "morning/afternoon/evening",
                        "estimated_duration": "время в минутах",
                        "deadline": "YYYY-MM-DD HH:MM",
                        "buffer_time": "время в минутах на непредвиденные обстоятельства",
                        "subtasks": [
                          {
                            "title": "название подзадачи",
                            "description": "детальное описание",
                            "duration": "время в минутах",
                            "order": "порядковый номер",
                            "dependencies": ["id предшествующих подзадач"]
                          }
                        ]
                      },
                      "resources": {
                        "energy_required": число от 1 до 10,
                        "focus_level": "high/medium/low",
                        "materials": ["необходимые ресурсы"],
                        "prerequisites": ["что нужно подготовить"],
                        "dependencies": ["на что влияет выполнение"],
                        "risks": ["возможные препятствия"],
                        "optimization_tips": ["рекомендации по оптимизации"]
                      }
                    }"""
                },
                {
                    "role": "user",
                    "content": f"Проанализируй задачу: {text}"
                }
            ]

            try:
                logger.info("Отправка запроса к OpenAI API")
                response = await self.client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Using GPT-3.5 for cost efficiency
                    messages=messages,
                    temperature=0.7,  # Balanced between creativity and consistency
                    max_tokens=1000,
                    response_format={"type": "json_object"}
                )

                self._last_request_time = datetime.now()
                logger.info("Получен ответ от OpenAI API")
                logger.debug(f"Ответ API: {response.choices[0].message.content}")

                result = json.loads(response.choices[0].message.content)

                # Cache the result
                self._cache[text] = result
                logger.info("Анализ задачи успешно завершен")
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

    def clear_cache(self):
        """Clear analysis results cache"""
        self._cache.clear()
        logger.debug("Кэш анализатора очищен")

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