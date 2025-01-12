"""Voice message handler service"""
import logging
import os
from pathlib import Path
from typing import Optional

from aiogram import Bot
from aiogram.types import Message, Voice

from pland.core.config import Config
from pland.services.voice.transcriber import AudioTranscriber

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Обработчик голосовых сообщений"""

    def __init__(self, bot: Bot, test_mode: bool = False):
        """
        Инициализация обработчика голосовых сообщений

        :param bot: Экземпляр бота для загрузки файлов
        :param test_mode: Режим тестирования
        """
        self.bot = bot
        self.temp_dir = Path(Config.BASE_DIR) / "temp" / "voice"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.transcriber = AudioTranscriber(test_mode=test_mode)
        logger.info(f"Voice handler initialized (test_mode: {test_mode})")

    async def process_voice_message(self, message: Message) -> Optional[str]:
        """
        Обработка голосового сообщения

        :param message: Сообщение с голосовым файлом
        :return: Текст, полученный из голосового сообщения
        """
        try:
            voice: Voice = message.voice
            if not voice:
                logger.warning("Получено сообщение без голосового файла")
                return None

            # Получаем информацию о файле
            file_id = voice.file_id
            logger.info(f"Получено голосовое сообщение, file_id: {file_id}")

            # Загружаем файл
            file = await self.bot.get_file(file_id)
            file_path = file.file_path

            # Создаём временный файл для сохранения
            temp_file = self.temp_dir / f"{file_id}.ogg"

            # Скачиваем файл
            await self.bot.download_file(file_path, temp_file)
            logger.info(f"Голосовое сообщение сохранено: {temp_file}")

            # Преобразуем в текст
            text = await self.transcriber.transcribe_audio(temp_file)

            # Удаляем временный файл
            os.unlink(temp_file)

            if text:
                logger.info(f"Голосовое сообщение успешно преобразовано в текст: {text[:100]}...")
                return text

            logger.warning("Не удалось преобразовать голосовое сообщение в текст")
            return None

        except Exception as e:
            logger.error(f"Ошибка при обработке голосового сообщения: {str(e)}", exc_info=True)
            return None

    async def cleanup(self):
        """Очистка временных файлов"""
        try:
            for file in self.temp_dir.glob("*"):
                os.unlink(file)
            logger.info("Временные файлы очищены")
        except Exception as e:
            logger.error(f"Ошибка при очистке временных файлов: {str(e)}", exc_info=True)