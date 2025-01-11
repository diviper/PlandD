"""Configuration module for PlanD"""
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Literal, Optional, ClassVar, TypedDict, Union

from dotenv import load_dotenv

# Project paths
ROOT_DIR = Path(__file__).parent.parent.parent.parent
ENV_PATH = ROOT_DIR / '.env'
LOG_DIR = ROOT_DIR / 'logs'

# Create necessary directories
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv(ENV_PATH)
logger = logging.getLogger(__name__)

# Log the loading of environment variables
logger.info(f"Loading environment from: {ENV_PATH}")
logger.info(f"OpenAI API Key loaded: {'*' * 5}{os.getenv('OPENAI_API_KEY', '')[-4:]}")
logger.info(f"Bot Token loaded: {'*' * 5}{os.getenv('BOT_TOKEN', '')[-4:]}")

# Get log level from environment or default to INFO
LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'DEBUG').upper())

def setup_logging(level: int = LOG_LEVEL) -> None:
    """
    Setup logging configuration for the entire application

    Args:
        level: The logging level to use (default: from environment or INFO)
    """
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s:%(lineno)d) - %(message)s'
    )

    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)

    file_handler = logging.FileHandler(LOG_DIR / 'pland.log')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)  # Always keep detailed logs in file

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Allow all logs to be processed
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Set specific levels for some modules
    logging.getLogger('pland.services.ai.analyzer').setLevel(logging.DEBUG)
    logging.getLogger('pland.bot').setLevel(logging.DEBUG)
    logging.getLogger('aiogram').setLevel(logging.INFO)

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

class ComplexityLevel(TypedDict):
    """Type definition for complexity level settings"""
    energy_cost: float
    focus_required: Literal['low', 'medium', 'high']

class TaskAnalysisSettings(TypedDict):
    """Type definition for task analysis settings"""
    min_break_duration: int
    max_task_duration: int
    energy_check_interval: int
    default_task_duration: int
    min_energy_level: int
    max_energy_level: int
    optimal_energy_threshold: int
    ai_temperature: float
    max_tokens: int
    response_format: str
    min_task_duration: int
    max_parallel_tasks: int
    break_between_tasks: int
    max_daily_work_hours: int
    urgent_threshold_hours: int
    high_priority_coefficient: float
    medium_priority_coefficient: float
    low_priority_coefficient: float
    cache_ttl: int
    max_cache_size: int
    complexity_levels: Dict[str, ComplexityLevel]

class SecuritySettings(TypedDict):
    """Type definition for security settings"""
    max_daily_tasks: int
    max_title_length: int
    max_description_length: int
    rate_limit_minutes: int
    max_api_retries: int
    retry_delay_seconds: int

@dataclass
class Config:
    """Application configuration with strong typing and validation"""

    # Base paths with proper typing
    BASE_DIR: ClassVar[Path] = Path(__file__).parent.parent
    DATABASE_DIR: ClassVar[Path] = BASE_DIR / "database" / "data"
    DATABASE_PATH: ClassVar[Path] = DATABASE_DIR / "tasks.db"

    # Create database directory
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    # API Tokens with validation
    BOT_TOKEN: ClassVar[str] = os.getenv('BOT_TOKEN', '')
    OPENAI_API_KEY: ClassVar[str] = os.getenv('OPENAI_API_KEY', '')

    @classmethod
    def __post_init__(cls):
        """Validate required environment variables"""
        if not cls.BOT_TOKEN:
            logger.error("BOT_TOKEN not found in environment variables")
            raise ValueError("BOT_TOKEN is required")

        if not cls.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY is required")

        logger.info("Configuration loaded successfully")

    # Time formats
    TIME_FORMAT: ClassVar[str] = "%H:%M"
    DATE_FORMAT: ClassVar[str] = "%Y-%m-%d"
    DATETIME_FORMAT: ClassVar[str] = f"{DATE_FORMAT} {TIME_FORMAT}"

    # Task priorities
    PRIORITY_HIGH: ClassVar[str] = "Высокий"
    PRIORITY_MEDIUM: ClassVar[str] = "Средний"
    PRIORITY_LOW: ClassVar[str] = "Низкий"

    # Notification settings
    NOTIFICATION_ADVANCE_TIME: ClassVar[int] = int(os.getenv('DEFAULT_REMINDER_TIME', '15'))

    # Notification templates
    NOTIFICATION_FORMATS: ClassVar[Dict[str, str]] = {
        "task_reminder": "🔔 Напоминание о задаче: {task_title}",
        "daily_summary": "📅 Ваш план на сегодня:",
        "energy_alert": "⚡️ Рекомендация по энергии: {message}",
        "break_time": "☕️ Время для перерыва!"
    }

    # Task analysis settings
    TASK_ANALYSIS_SETTINGS: ClassVar[Dict[str, Union[int, float, str, Dict]]] = {
        "min_break_duration": 15,
        "max_task_duration": 180,
        "energy_check_interval": 120,
        "default_task_duration": 60,
        "min_energy_level": 1,
        "max_energy_level": 10,
        "optimal_energy_threshold": 7,
        "ai_temperature": float(os.getenv('TASK_ANALYSIS_TEMPERATURE', '0.7')),
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
        "complexity_levels": {
            "easy": {"energy_cost": 0.7, "focus_required": "low"},
            "medium": {"energy_cost": 1.0, "focus_required": "medium"},
            "hard": {"energy_cost": 1.5, "focus_required": "high"}
        }
    }

    # Security settings
    SECURITY_SETTINGS: ClassVar[Dict[str, int]] = {
        "max_daily_tasks": int(os.getenv('MAX_DAILY_TASKS', '50')),
        "max_title_length": 200,
        "max_description_length": 1000,
        "rate_limit_minutes": 1,
        "max_api_retries": int(os.getenv('MAX_API_RETRIES', '3')),
        "retry_delay_seconds": int(os.getenv('RETRY_DELAY_SECONDS', '5'))
    }

    # Quiet hours settings
    QUIET_HOURS_START: ClassVar[str] = os.getenv('QUIET_HOURS_START', '23:00')
    QUIET_HOURS_END: ClassVar[str] = os.getenv('QUIET_HOURS_END', '07:00')

    # Bot commands
    COMMANDS: ClassVar[Dict[str, str]] = {
        "start": "Начать работу с ботом",
        "help": "Показать справку",
        "add": "Добавить новую задачу",
        "list": "Показать список задач",
        "upcoming": "Показать ближайшие задачи",
        "done": "Отметить задачу как выполненную",
        "delete": "Удалить задачу",
        "analyze": "Проанализировать текущие задачи",
        "optimize": "Оптимизировать расписание",
        "energy": "Показать рекомендации по энергии"
    }