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

    # Database settings
    DATABASE_PATH = os.path.join(ROOT_DIR, os.getenv('DATABASE_PATH', 'data/tasks.db'))

    # Task settings
    MIN_TASK_LENGTH = int(os.getenv('MIN_TASK_LENGTH', '10'))
    MAX_TASK_LENGTH = int(os.getenv('MAX_TASK_LENGTH', '1000'))
    DEFAULT_REMINDER_MINUTES = int(os.getenv('DEFAULT_REMINDER_MINUTES', '30'))
    MAX_REMINDERS_PER_TASK = int(os.getenv('MAX_REMINDERS_PER_TASK', '5'))

    # OpenAI settings
    OPENAI_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 1000
    TEMPERATURE = float(os.getenv('TASK_ANALYSIS_TEMPERATURE', '0.7'))

    # Task Analysis Settings
    TASK_ANALYSIS_SETTINGS = {
        "min_break_duration": 15,
        "max_task_duration": 180,
        "energy_check_interval": 120,
        "default_task_duration": 60,
        "min_energy_level": 1,
        "max_energy_level": 10,
        "optimal_energy_threshold": 7,
        "max_tokens": 1000,
        "response_format": "json_object",
        "min_task_duration": 10,
        "max_parallel_tasks": 3,
        "break_between_tasks": 5,
        "max_daily_work_hours": 12,
        "urgent_threshold_hours": 24,
        "high_priority_coefficient": 1.5,
        "medium_priority_coefficient": 1.0,
        "low_priority_coefficient": 0.7,
        "cache_ttl": int(os.getenv('CACHE_TTL', '3600')),
        "max_cache_size": int(os.getenv('MAX_CACHE_SIZE', '1000')),
    }

    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Time settings
    QUIET_HOURS_START = os.getenv('QUIET_HOURS_START', '23:00')
    QUIET_HOURS_END = os.getenv('QUIET_HOURS_END', '07:00')

def setup_logging(level: str = None):
    """Setup logging configuration"""
    if level is None:
        level = Config.LOG_LEVEL
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_DIR / 'bot.log')
        ]
    )

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)