import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    """
    Конфигурация приложения
    """
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'tasks.db')