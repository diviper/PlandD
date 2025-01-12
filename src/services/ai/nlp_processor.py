"""Модуль обработки естественного языка"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import re

from openai import AsyncOpenAI

from src.core.config import Config

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Обработчик естественного языка для анализа сообщений пользователя"""

    def __init__(self):
        """Инициализация обработчика"""
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("NLP процессор инициализирован")

    async def process_message(self, text: str) -> Dict:
        """
        Обрабатывает сообщение пользователя и извлекает структурированную информацию

        Args:
            text: Текст сообщения пользователя

        Returns:
            Dict с извлеченной информацией
        """
        try:
            # Предварительная обработка текста
            cleaned_text = self._preprocess_text(text)
            
            # Извлекаем временные метки
            time_info = self._extract_time_info(cleaned_text)
            
            # Анализируем через AI
            analysis = await self._analyze_with_ai(cleaned_text, time_info)
            
            return analysis

        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {str(e)}", exc_info=True)
            return {}

    def _preprocess_text(self, text: str) -> str:
        """Предварительная обработка текста"""
        # Приводим к нижнему регистру
        text = text.lower()
        
        # Удаляем лишние пробелы
        text = ' '.join(text.split())
        
        # Заменяем часто используемые сокращения
        replacements = {
            'пн': 'понедельник',
            'вт': 'вторник',
            'ср': 'среда',
            'чт': 'четверг',
            'пт': 'пятница',
            'сб': 'суббота',
            'вс': 'воскресенье',
        }
        for short, full in replacements.items():
            text = text.replace(short, full)
        
        return text

    def _extract_time_info(self, text: str) -> Dict:
        """Извлекает информацию о времени из текста"""
        time_info = {
            'explicit_time': None,
            'relative_time': None,
            'duration': None,
            'weekday': None
        }

        # Поиск явного указания времени (например, "в 15:00")
        time_pattern = r'в (\d{1,2}[:\.]\d{2})'
        if match := re.search(time_pattern, text):
            time_str = match.group(1).replace('.', ':')
            try:
                time_info['explicit_time'] = datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                pass

        # Поиск относительного времени (например, "через 2 часа")
        relative_pattern = r'через (\d+) (час|часа|часов|минут|минуты)'
        if match := re.search(relative_pattern, text):
            amount = int(match.group(1))
            unit = match.group(2)
            if 'час' in unit:
                time_info['relative_time'] = timedelta(hours=amount)
            elif 'минут' in unit:
                time_info['relative_time'] = timedelta(minutes=amount)

        # Поиск длительности (например, "на 30 минут")
        duration_pattern = r'на (\d+) (час|часа|часов|минут|минуты)'
        if match := re.search(duration_pattern, text):
            amount = int(match.group(1))
            unit = match.group(2)
            if 'час' in unit:
                time_info['duration'] = amount * 60
            elif 'минут' in unit:
                time_info['duration'] = amount

        # Поиск дня недели
        weekdays = {
            'понедельник': 0, 'вторник': 1, 'среда': 2, 'четверг': 3,
            'пятница': 4, 'суббота': 5, 'воскресенье': 6
        }
        for day, num in weekdays.items():
            if day in text:
                time_info['weekday'] = num
                break

        return time_info

    async def _analyze_with_ai(self, text: str, time_info: Dict) -> Dict:
        """Анализирует текст с помощью AI"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты - эксперт по анализу задач и планированию. "
                        "Проанализируй сообщение пользователя и извлеки следующую информацию:\n"
                        "1. Тип задачи (встреча, работа, личное и т.д.)\n"
                        "2. Приоритет (высокий/средний/низкий)\n"
                        "3. Требуемые ресурсы или подготовка\n"
                        "4. Возможные зависимости от других задач\n"
                        "5. Оценка сложности (1-10)\n"
                        "Верни результат в формате JSON."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Текст сообщения: {text}\n"
                        f"Информация о времени: {json.dumps(time_info, ensure_ascii=False)}"
                    )
                }
            ]

            response = await self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                temperature=Config.TEMPERATURE,
                response_format={"type": "json_object"}
            )

            analysis = json.loads(response.choices[0].message.content)
            
            # Добавляем извлеченную информацию о времени
            analysis.update({
                "time_info": time_info
            })

            return analysis

        except Exception as e:
            logger.error(f"Ошибка AI анализа: {str(e)}", exc_info=True)
            return {}
