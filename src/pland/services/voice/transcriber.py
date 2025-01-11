"""Voice transcription service"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class VoiceTranscriber:
    """Сервис преобразования голоса в текст (временно отключен)"""

    def __init__(self):
        """Initialize transcriber"""
        logger.warning("Функционал преобразования голоса в текст временно отключен")

    async def transcribe_voice(self, file_path: str) -> Optional[str]:
        """
        Преобразование голосового сообщения в текст
        Временно отключено до выбора оптимальной модели

        Args:
            file_path: Путь к файлу с голосовым сообщением

        Returns:
            Optional[str]: Текст сообщения или None в случае ошибки
        """
        logger.warning("Функционал преобразования голоса в текст временно отключен")
        return None
