"""AI services for PlanD"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.core.config import Config
from src.database.database import Database
from src.database.models import Plan, PlanStep, PlanProgress, UserPreferences

logger = logging.getLogger(__name__)

class AIService:
    """Единый сервис для работы с AI"""
    
    def __init__(self, db: Database):
        """Initialize AI service with database connection"""
        if not Config.OPENAI_API_KEY:
            logger.error("OpenAI API key not found")
            raise ValueError("OpenAI API key is required")
            
        self.db = db
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("AI service initialized successfully")

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def analyze_plan(self, text: str, plan_type: str) -> Optional[Dict]:
        """
        Анализ описания плана и создание структурированного плана

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

    async def analyze_progress(self, plan_id: int) -> Optional[Dict]:
        """
        Анализ прогресса выполнения плана

        Args:
            plan_id: ID плана для анализа

        Returns:
            Dict с анализом прогресса или None при ошибке
        """
        try:
            # Получаем план и его прогресс
            plan_data = await self.db.get_plan(plan_id)
            if not plan_data:
                logger.error(f"План {plan_id} не найден")
                return None

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Проанализируй прогресс выполнения плана и предложи улучшения.\n"
                        "Верни JSON в формате:\n"
                        "{\n"
                        "  'completion_rate': процент выполнения,\n"
                        "  'status': 'on_track/delayed/at_risk',\n"
                        "  'analysis': 'общий анализ прогресса',\n"
                        "  'blockers': ['обнаруженные проблемы'],\n"
                        "  'recommendations': ['конкретные предложения'],\n"
                        "  'next_steps': ['следующие шаги']\n"
                        "}"
                    )
                },
                {
                    "role": "user",
                    "content": f"План: {json.dumps(plan_data)}"
                }
            ]

            response = await self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            result = response.choices[0].message.content
            analysis = json.loads(result)
            
            logger.info(f"Прогресс плана {plan_id} проанализирован")
            return analysis

        except Exception as e:
            logger.error(f"Ошибка при анализе прогресса: {str(e)}")
            return None

    async def learn_patterns(self, user_id: int) -> Optional[Dict]:
        """
        Анализ паттернов пользователя для улучшения планирования

        Args:
            user_id: ID пользователя

        Returns:
            Dict с паттернами или None при ошибке
        """
        try:
            # Получаем данные пользователя
            session = self.db.get_session()
            prefs = session.query(UserPreferences).filter_by(user_id=user_id).first()
            if not prefs:
                logger.warning(f"Предпочтения пользователя {user_id} не найдены")
                return None

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Проанализируй паттерны пользователя и предложи оптимизации.\n"
                        "Верни JSON в формате:\n"
                        "{\n"
                        "  'productivity_patterns': {\n"
                        "    'peak_hours': ['время максимальной продуктивности'],\n"
                        "    'optimal_duration': 'оптимальная длительность задач',\n"
                        "    'break_patterns': 'оптимальные перерывы'\n"
                        "  },\n"
                        "  'success_factors': ['факторы успеха'],\n"
                        "  'risk_factors': ['факторы риска'],\n"
                        "  'recommendations': ['рекомендации']\n"
                        "}"
                    )
                },
                {
                    "role": "user",
                    "content": "Предпочтения: " + json.dumps({
                        'work_hours': prefs.preferred_work_hours,
                        'peak_hours': prefs.peak_productivity_hours,
                        'energy_curve': prefs.typical_energy_curve,
                        'success_rate': prefs.avg_task_completion_rate,
                        'distractions': prefs.common_distractions
                    })
                }
            ]

            response = await self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            result = response.choices[0].message.content
            patterns = json.loads(result)
            
            logger.info(f"Паттерны пользователя {user_id} проанализированы")
            return patterns

        except Exception as e:
            logger.error(f"Ошибка при анализе паттернов: {str(e)}")
            return None
        finally:
            session.close()

    async def suggest_improvements(self, plan_id: int) -> Optional[Dict]:
        """
        Предложение улучшений для плана на основе прогресса и паттернов

        Args:
            plan_id: ID плана

        Returns:
            Dict с предложениями или None при ошибке
        """
        try:
            # Получаем план и прогресс
            plan_data = await self.db.get_plan(plan_id)
            if not plan_data:
                logger.error(f"План {plan_id} не найден")
                return None

            # Получаем паттерны пользователя
            patterns = await self.learn_patterns(plan_data['user_id'])
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "На основе прогресса и паттернов предложи улучшения плана.\n"
                        "Верни JSON в формате:\n"
                        "{\n"
                        "  'schedule_adjustments': ['предложения по расписанию'],\n"
                        "  'step_modifications': ['изменения в шагах'],\n"
                        "  'additional_steps': ['новые шаги'],\n"
                        "  'risk_mitigations': ['снижение рисков'],\n"
                        "  'motivation_boosters': ['повышение мотивации']\n"
                        "}"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"План: {json.dumps(plan_data)}\n"
                        f"Паттерны: {json.dumps(patterns) if patterns else '{}'}"
                    )
                }
            ]

            response = await self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            result = response.choices[0].message.content
            improvements = json.loads(result)
            
            logger.info(f"Сгенерированы предложения по улучшению плана {plan_id}")
            return improvements

        except Exception as e:
            logger.error(f"Ошибка при генерации предложений: {str(e)}")
            return None
