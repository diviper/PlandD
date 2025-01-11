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

        # Логируем детали роутера
        logger.debug(f"Основной роутер: {router.name}")

        # Регистрируем базовые обработчики
        base_router = Router(name="base_router")
        register_base_handlers(base_router)
        router.include_router(base_router)
        logger.info("✓ Зарегистрированы базовые обработчики")
        logger.debug(f"Базовый роутер добавлен: {base_router.name}")

        # Регистрируем обработчики задач
        tasks_router = Router(name="tasks_router")
        register_task_handlers(tasks_router, db)  # Изменено здесь
        router.include_router(tasks_router)
        logger.info("✓ Зарегистрированы обработчики задач")
        logger.debug(f"Роутер задач добавлен: {tasks_router.name}")

        # Проверяем количество зарегистрированных обработчиков
        handlers_count = len(router.message.handlers)
        logger.info(f"Всего зарегистрировано обработчиков: {handlers_count}")

        logger.info("=== Регистрация обработчиков завершена успешно ===")
    except Exception as e:
        logger.error(f"❌ Ошибка при регистрации обработчиков: {str(e)}", exc_info=True)
        raise
