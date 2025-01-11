"""Bot package initialization"""
import logging

logger = logging.getLogger(__name__)

from .handlers import register_handlers
from .bot import run_bot

__all__ = ["register_handlers", "run_bot"]