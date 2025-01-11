"""Notifier service for sending reminders"""
import logging
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

logger = logging.getLogger(__name__)

class Notifier:
    """Сервис отправки уведомлений"""

    def __init__(self, bot: Bot):
        """
        Инициализация сервиса уведомлений

        :param bot: Экземпляр бота для отправки сообщений
        """
        self.bot = bot
        logger.info("Notifier service initialized")

    async def send_notification(self, user_id: int, message: str, 
                              reply_markup: Optional[dict] = None) -> bool:
        """
        Отправка уведомления пользователю

        :param user_id: ID пользователя
        :param message: Текст сообщения
        :param reply_markup: Опциональная клавиатура или кнопки
        :return: True если сообщение отправлено успешно
        """
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                reply_markup=reply_markup
            )
            return True
        except TelegramAPIError as e:
            logger.error(f"Failed to send notification to user {user_id}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending notification: {str(e)}")
            return False

    async def send_error_notification(self, user_id: int, error_message: str) -> None:
        """
        Отправка уведомления об ошибке

        :param user_id: ID пользователя
        :param error_message: Сообщение об ошибке
        """
        message = f"❌ Произошла ошибка:\n{error_message}"
        await self.send_notification(user_id, message)

    async def send_success_notification(self, user_id: int, message: str) -> None:
        """
        Отправка уведомления об успешном выполнении

        :param user_id: ID пользователя
        :param message: Текст сообщения
        """
        formatted_message = f"✅ {message}"
        await self.send_notification(user_id, formatted_message)
