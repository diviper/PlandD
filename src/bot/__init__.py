"""Bot package initialization"""
import logging
import sys
sys.stdout.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)

from .handlers import register_task_handlers
from .bot import run_bot

__all__ = ["register_task_handlers", "run_bot"]