"""Handlers package initialization"""
import logging
from aiogram import Router
from pland.database.database import Database

from .base import register_base_handlers
from .tasks import register_task_handlers

logger = logging.getLogger(__name__)

def register_handlers(router: Router, db: Database):
    """Register all message handlers"""
    try:
        logger.info("=== Регистрация обработчиков команд ===")

        # Регистрируем базовые обработчики
        base_router = Router(name="base_router")
        register_base_handlers(base_router)
        router.include_router(base_router)
        logger.info("✓ Зарегистрированы базовые обработчики")

        # Регистрируем обработчики задач
        tasks_router = Router(name="tasks_router")
        register_task_handlers(tasks_router, db)
        router.include_router(tasks_router)
        logger.info("✓ Зарегистрированы обработчики задач")

        logger.info("=== Регистрация обработчиков завершена успешно ===")
    except Exception as e:
        logger.error(f"❌ Ошибка при регистрации обработчиков: {str(e)}", exc_info=True)
        raise