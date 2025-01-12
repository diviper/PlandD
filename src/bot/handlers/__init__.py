"""Handlers initialization"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import logging
from aiogram import Router
from src.database.database import Database
from .base import register_base_handlers
from .tasks import register_task_handlers
from .plan_handler import register_handlers as register_plan_handlers

logger = logging.getLogger(__name__)

def register_handlers(dp: Router, db: Database):
    """Register all handlers"""
    logger.info("=== Регистрация обработчиков команд ===")
    
    # Регистрация базовых обработчиков
    logger.info("Регистрация базовых обработчиков...")
    register_base_handlers(dp)
    logger.info("[OK] Базовые обработчики зарегистрированы")
    
    # Регистрация обработчиков задач
    logger.info("Регистрация обработчиков задач...")
    register_task_handlers(dp, db)
    logger.info("[OK] Обработчики задач зарегистрированы")
    
    # Регистрация обработчиков планов
    logger.info("Регистрация обработчиков планов...")
    register_plan_handlers(dp, db)
    logger.info("[OK] Обработчики планов зарегистрированы")
    
    # Подсчет общего количества обработчиков
    total_handlers = len(dp.message.handlers) + len(dp.callback_query.handlers)
    logger.info(f"Всего зарегистрировано обработчиков: {total_handlers}")
    logger.info("=== Регистрация обработчиков завершена успешно ===")