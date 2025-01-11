"""Voice message handler module"""
import logging

from .transcriber import VoiceTranscriber

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Обработчик голосовых сообщений (временно отключен)"""

    def __init__(self):
        """Initialize voice handler"""
        self.transcriber = VoiceTranscriber()
        logger.warning("Функционал голосовых сообщений временно отключен")

    async def process_voice_message(self, voice_data: bytes, user_id: int) -> Optional[str]:
        """
        Обработка голосового сообщения
        Временно отключена до выбора оптимальной модели

        Args:
            voice_data: Байты голосового сообщения
            user_id: ID пользователя

        Returns:
            Optional[str]: Распознанный текст или None в случае ошибки
        """
        logger.warning("Функционал голосовых сообщений временно отключен")
        return None