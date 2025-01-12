"""Configuration module for PlanD"""
import logging
import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Project paths
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_PATH = ROOT_DIR / '.env'
LOG_DIR = ROOT_DIR / 'logs'

# Create necessary directories
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables with explicit path
load_dotenv(ENV_PATH)

class Config:
    """Configuration class"""
    # Bot settings
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        raise ValueError('Missing BOT_TOKEN in environment variables')

    # OpenAI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError('Missing OPENAI_API_KEY in environment variables')

    OPENAI_MODEL = "gpt-4-1106-preview"
    MAX_TOKENS = 800
    TEMPERATURE = float(os.getenv('TASK_ANALYSIS_TEMPERATURE', '0.7'))

    # Cache settings
    CACHE_EXPIRY = 3600
    MAX_CACHE_ENTRIES = int(os.getenv('MAX_CACHE_SIZE', '1000'))

    # Database settings
    database_default = str(ROOT_DIR / 'data' / 'tasks.db')
    DATABASE_PATH = os.path.abspath(os.getenv('DATABASE_PATH', database_default))

    # Scheduler settings
    PRIORITY_INTERVALS = {
        'high': 5,     # Проверять каждые 5 минут
        'medium': 15,  # Проверять каждые 15 минут
        'low': 30      # Проверять каждые 30 минут
    }

    # Task settings
    MIN_TASK_LENGTH = int(os.getenv('MIN_TASK_LENGTH', '10'))
    MAX_TASK_LENGTH = int(os.getenv('MAX_TASK_LENGTH', '1000'))
    DEFAULT_REMINDER_MINUTES = int(os.getenv('DEFAULT_REMINDER_MINUTES', '30'))
    MAX_REMINDERS_PER_TASK = int(os.getenv('MAX_REMINDERS_PER_TASK', '5'))

    # Task Analysis Settings
    TASK_ANALYSIS_SETTINGS = {
        "min_break_duration": 15,
        "max_task_duration": 180,
        "energy_check_interval": 120,
        "default_task_duration": 60,
        "min_energy_level": 1,
        "max_energy_level": 10,
        "default_energy_level": 5
    }

    # Reminder Settings
    REMINDER_SETTINGS = {
        "default_advance_notice": 15,
        "min_advance_notice": 5,
        "max_advance_notice": 60,
        "check_interval": 60
    }

    # Logging Settings
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.path.join(LOG_DIR, 'pland.log')

    # Response timeouts (seconds)
    API_TIMEOUT = 30
    COMMAND_TIMEOUT = 60

def setup_logging(level: str = None):
    """Setup logging configuration"""
    log_level = level or Config.LOG_LEVEL
    logging.basicConfig(
        level=log_level,
        format=Config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)