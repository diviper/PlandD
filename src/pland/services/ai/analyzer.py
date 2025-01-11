"""Task analyzer using OpenAI API"""
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
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

class TaskAnalyzer:
    """Анализатор задач с использованием OpenAI API"""

    def __init__(self):
        """Initialize TaskAnalyzer with OpenAI client"""
        if not Config.OPENAI_API_KEY:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key is required")

        logger.info("Initializing TaskAnalyzer...")
        logger.debug(f"Using OpenAI API key ending in: ...{Config.OPENAI_API_KEY[-4:]}")

        try:
            self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
            self._cache = {}
            self._last_request_time = datetime.min
            self._request_semaphore = asyncio.Semaphore(3)
            logger.info("TaskAnalyzer initialization completed successfully")
        except Exception as e:
            logger.error(f"Error initializing TaskAnalyzer: {str(e)}", exc_info=True)
            raise

    async def test_api_connection(self):
        """Test OpenAI API connection"""
        try:
            logger.info("Testing OpenAI API connection...")
            logger.debug("Sending test request to OpenAI API")

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )

            logger.debug(f"Received response from API test: {response}")

            if response and response.choices:
                logger.info("✓ OpenAI API connection test successful")
                return True

            logger.error("OpenAI API connection test failed: Empty response")
            return False

        except Exception as e:
            logger.error(f"OpenAI API connection test failed: {str(e)}", exc_info=True)
            return False

    async def analyze_task(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze task text and return structured result
        """
        try:
            logger.info(f"Starting task analysis for text: {text[:100]}...")

            # Check cache
            if text in self._cache:
                logger.info("Found cached result")
                return self._cache[text]

            # Apply rate limiting
            now = datetime.now()
            time_since_last_request = (now - self._last_request_time).total_seconds()
            if time_since_last_request < 1.0:
                delay = 1.0 - time_since_last_request
                logger.debug(f"Applying rate limit delay: {delay} seconds")
                await asyncio.sleep(delay)

            async with self._request_semaphore:
                logger.info("Preparing OpenAI API request")

                system_prompt = {
                    "role": "system",
                    "content": """Ты опытный планировщик задач. Проанализируй задачу и создай структурированный план.
Учитывай следующие аспекты:
1. Приоритет (high/medium/low)
2. Сроки выполнения
3. Декомпозиция на подзадачи
4. Энергозатратность (1-10)
5. Оптимальное время выполнения

Верни результат строго в формате JSON:
{
  "title": "краткое название",
  "priority": "high/medium/low",
  "due_date": "YYYY-MM-DD HH:mm",
  "estimated_total_time": 30,
  "energy_level": 5,
  "tasks": [
    {
      "title": "название подзадачи",
      "description": "описание",
      "priority": "high/medium/low",
      "estimated_duration": 30,
      "energy_level": 5
    }
  ]
}"""
                }

                user_prompt = {
                    "role": "user",
                    "content": f"Проанализируй задачу: {text}\n\nТекущее время: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }

                logger.info("Sending request to OpenAI API")
                try:
                    logger.debug(f"System prompt: {system_prompt}")
                    logger.debug(f"User prompt: {user_prompt}")

                    response = await self.client.chat.completions.create(
                        model="gpt-4",
                        messages=[system_prompt, user_prompt],
                        response_format={"type": "json_object"},
                        temperature=Config.TASK_ANALYSIS_SETTINGS["ai_temperature"]
                    )

                    self._last_request_time = datetime.now()
                    logger.info("Received response from OpenAI API")
                    logger.debug(f"Raw API response: {response.choices[0].message.content}")

                except APIError as api_error:
                    logger.error(f"OpenAI API Error: {str(api_error)}")
                    if "invalid_api_key" in str(api_error).lower():
                        logger.error("Possible invalid API key")
                    return None
                except Exception as e:
                    logger.error(f"Error in API request: {str(e)}", exc_info=True)
                    return None

                try:
                    logger.info("Parsing API response")
                    result = json.loads(response.choices[0].message.content)
                    logger.debug(f"Parsed result: {result}")

                    # Validate required fields
                    required_fields = ['title', 'priority', 'due_date']
                    if not all(field in result for field in required_fields):
                        missing = [f for f in required_fields if f not in result]
                        logger.error(f"Missing required fields in API response: {missing}")
                        return None

                    # Convert date
                    try:
                        result['due_date'] = datetime.strptime(
                            result['due_date'],
                            '%Y-%m-%d %H:%M'
                        )
                        logger.debug(f"Converted due_date: {result['due_date']}")
                    except ValueError as e:
                        logger.error(f"Invalid date format: {result.get('due_date')}, error: {str(e)}")
                        result['due_date'] = datetime.now() + timedelta(days=1)
                        logger.info(f"Using default due date: {result['due_date']}")

                    # Cache result
                    self._cache[text] = result
                    logger.info("Task analysis completed successfully")
                    return result

                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {str(e)}")
                    logger.debug(f"Problematic JSON: {response.choices[0].message.content}")
                    return None

        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in task analysis: {str(e)}", exc_info=True)
            return None
        finally:
            logger.info("=== Task analysis completed ===")

    def clear_cache(self):
        """Clear analysis results cache"""
        self._cache.clear()
        logger.debug("Task analyzer cache cleared")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError))
    )
    async def _make_api_request(self, messages: List[Dict], max_retries: int = 3):
        """Make API request with retries"""
        try:
            logger.debug(f"Making API request (attempt {max_retries})")
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=Config.TASK_ANALYSIS_SETTINGS["ai_temperature"]
            )
            logger.debug("API request successful")
            return response
        except Exception as e:
            logger.error(f"API request failed: {str(e)}", exc_info=True)
            raise

from typing import List