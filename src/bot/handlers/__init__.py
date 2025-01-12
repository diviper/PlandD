"""Handlers package initialization"""
import logging
from aiogram import Router
from src.database.database import Database

from .base import register_base_handlers
from .tasks import register_task_handlers

logger = logging.getLogger(__name__)

def register_handlers(router: Router, db: Database):
    """Register all message handlers"""
    try:
        logger.info("=== Регистрация обработчиков команд ===")

        # Регистрируем базовые обработчики
        logger.info("Регистрация базовых обработчиков...")
        register_base_handlers(router)
        logger.info("✓ Базовые обработчики зарегистрированы")

        # Регистрируем обработчики задач
        logger.info("Регистрация обработчиков задач...")
        register_task_handlers(router, db)
        logger.info("✓ Обработчики задач зарегистрированы")

        # Проверяем количество зарегистрированных обработчиков
        handlers_count = len(router.observers['message'].handlers)
        logger.info(f"Всего зарегистрировано обработчиков: {handlers_count}")

        logger.info("=== Регистрация обработчиков завершена успешно ===")
    except Exception as e:
        logger.error(f"❌ Ошибка при регистрации обработчиков: {str(e)}", exc_info=True)
        raise