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

    def __init__(self, test_mode: bool = False):
        """Initialize TaskAnalyzer with OpenAI client"""
        if not Config.OPENAI_API_KEY:
            logger.error("OpenAI API key не найден")
            raise ValueError("OpenAI API key обязателен")

        self.test_mode = test_mode
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info(f"TaskAnalyzer инициализирован (test_mode: {test_mode})")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
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

            if self.test_mode:
                logger.info("Работаем в тестовом режиме, возвращаем тестовый ответ")
                return {
                    "priority": {
                        "level": "high",
                        "reason": "Тестовый режим",
                        "urgency": "срочно",
                        "importance": "важно"
                    },
                    "schedule": {
                        "optimal_time": "morning",
                        "estimated_duration": 60,
                        "deadline": "2025-01-11 15:00",
                        "buffer_time": 30,
                        "subtasks": [
                            {
                                "title": "Тестовая подзадача",
                                "description": "Описание тестовой подзадачи",
                                "duration": 30,
                                "order": 1
                            }
                        ]
                    },
                    "resources": {
                        "energy_required": 8,
                        "focus_level": "high",
                        "materials": ["тест"],
                        "prerequisites": [],
                        "dependencies": [],
                        "risks": [],
                        "optimization_tips": []
                    }
                }

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты - эксперт по анализу задач. Проанализируй задачу и верни результат строго в таком JSON формате:\n"
                        "{\n"
                        "  'priority': {\n"
                        "    'level': 'high/medium/low',\n"
                        "    'reason': 'причина приоритета',\n"
                        "    'urgency': 'срочно/не срочно',\n"
                        "    'importance': 'важно/средне/не важно'\n"
                        "  },\n"
                        "  'schedule': {\n"
                        "    'optimal_time': 'morning/afternoon/evening',\n"
                        "    'estimated_duration': число_минут,\n"
                        "    'deadline': 'YYYY-MM-DD HH:MM',\n"
                        "    'buffer_time': число_минут,\n"
                        "    'subtasks': [\n"
                        "      {\n"
                        "        'title': 'название подзадачи',\n"
                        "        'description': 'описание',\n"
                        "        'duration': число_минут,\n"
                        "        'order': порядковый_номер\n"
                        "      }\n"
                        "    ]\n"
                        "  },\n"
                        "  'resources': {\n"
                        "    'energy_required': число_от_1_до_10,\n"
                        "    'focus_level': 'high/medium/low',\n"
                        "    'materials': ['материал1', 'материал2'],\n"
                        "    'prerequisites': ['требование1', 'требование2'],\n"
                        "    'risks': ['риск1', 'риск2']\n"
                        "  }\n"
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
                max_tokens=500,
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
            if self.test_mode:
                logger.info("Тестовый режим: подключение к API считается успешным")
                return True

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