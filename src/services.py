import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from openai import AsyncOpenAI

from pland.config import Config
from pland.db import Database, Task

class TaskService:
    def __init__(self, bot: Bot = None):
        self.bot = bot
        self.db = Database()
        self.ai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    async def analyze_task(self, text: str) -> str:
        try:
            response = await self.ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Дай краткое описание задачи"},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content or "Не удалось проанализировать"
        except Exception as e:
            print(f"Ошибка анализа задачи: {e}")
            return "Не удалось проанализировать задачу"

    async def create_plan(self, text: str) -> dict:
        try:
            return {"priority": "medium"}
        except Exception as e:
            print(f"Ошибка планирования: {e}")
            return {"priority": "medium"}

    async def check_reminders(self, chat_id: int):
        """
        Проверка и отправка напоминаний
        """
        now = datetime.now()
        tasks = self.db.get_tasks_with_reminders()
        
        for task in tasks:
            try:
                # task[4] - это столбец reminder_time
                reminder_time = datetime.fromisoformat(task[4])
                if reminder_time <= now:
                    await self.send_reminder(chat_id, task)
                    
                    # Пометка задачи как выполненной после напоминания
                    cursor = self.db.conn.cursor()
                    cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task[0],))
                    self.db.conn.commit()
            except Exception as e:
                print(f"Ошибка обработки напоминания: {e}")

    async def send_reminder(self, chat_id: int, task):
        """
        Отправка напоминания о задаче
        """
        try:
            if not self.bot:
                print("Бот не инициализирован для отправки напоминаний")
                return

            message = f"🔔 Напоминание: {task[1]}"  # task[1] - описание задачи
            await self.bot.send_message(chat_id, message)
        except Exception as e:
            print(f"Не удалось отправить напоминание: {e}")