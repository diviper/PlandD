"""Voice message handler module"""
import logging
import os
from typing import Optional, Tuple
import aiofiles
import aiohttp
from openai import AsyncOpenAI, APIError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from pland.core.config import Config

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Обработчик голосовых сообщений с использованием OpenAI Whisper"""

    def __init__(self):
        """Initialize voice handler with OpenAI client"""
        if not Config.OPENAI_API_KEY:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.voice_dir = os.path.join(Config.BASE_DIR, "temp", "voice")
        os.makedirs(self.voice_dir, exist_ok=True)
        logger.info("VoiceHandler initialized successfully")
        logger.debug(f"Директория для голосовых файлов: {self.voice_dir}")

    async def process_voice_message(self, voice_file_url: str, file_id: str) -> Tuple[bool, Optional[str]]:
        """
        Обработка голосового сообщения: загрузка, сохранение и транскрибация

        Args:
            voice_file_url: URL файла голосового сообщения
            file_id: Уникальный идентификатор файла

        Returns:
            Tuple[bool, Optional[str]]: (успех операции, текст сообщения или None)
        """
        try:
            logger.info(f"Начата обработка голосового сообщения: {file_id}")
            logger.debug(f"URL файла: {voice_file_url}")

            # Загрузка и сохранение файла
            file_path = await self._download_voice_file(voice_file_url, file_id)
            if not file_path:
                logger.error("Не удалось загрузить голосовой файл")
                return False, None

            logger.info(f"Файл успешно загружен: {file_path}")
            logger.debug(f"Размер файла: {os.path.getsize(file_path)} байт")

            # Транскрибация
            text = await self._transcribe_voice(file_path)
            if not text:
                logger.error("Не удалось транскрибировать голосовое сообщение")
                return False, None

            logger.info("Голосовое сообщение успешно транскрибировано")
            logger.debug(f"Результат транскрибации: {text[:100]}...")  # Логируем только начало текста

            # Очистка временного файла
            try:
                os.remove(file_path)
                logger.debug(f"Временный файл удален: {file_path}")
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл {file_path}: {str(e)}")

            return True, text

        except Exception as e:
            logger.error(f"Ошибка при обработке голосового сообщения: {str(e)}", exc_info=True)
            return False, None

    async def _download_voice_file(self, url: str, file_id: str) -> Optional[str]:
        """
        Загрузка голосового файла

        Args:
            url: URL файла
            file_id: Идентификатор файла

        Returns:
            Optional[str]: Путь к сохраненному файлу или None
        """
        try:
            file_path = os.path.join(self.voice_dir, f"{file_id}.ogg")
            logger.info(f"Загрузка файла из: {url}")

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка при загрузке файла: {response.status}")
                        return None

                    async with aiofiles.open(file_path, mode='wb') as f:
                        await f.write(await response.read())

            logger.info(f"Файл успешно сохранен: {file_path}")
            logger.debug(f"Размер загруженного файла: {os.path.getsize(file_path)} байт")
            return file_path

        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сетевого подключения при загрузке файла: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при загрузке файла: {str(e)}", exc_info=True)
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(APIError)
    )
    async def _transcribe_voice(self, file_path: str) -> Optional[str]:
        """
        Транскрибация голосового сообщения с помощью OpenAI Whisper

        Args:
            file_path: Путь к файлу для транскрибации

        Returns:
            Optional[str]: Текст сообщения или None в случае ошибки
        """
        try:
            logger.info(f"Начата транскрибация файла: {file_path}")
            logger.debug(f"Используется модель: whisper-1")

            with open(file_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ru",
                    response_format="text"
                )

            if not transcript:
                logger.error("Получен пустой результат транскрибации")
                return None

            logger.info("Транскрибация успешно завершена")
            logger.debug(f"Длина транскрибированного текста: {len(transcript)} символов")
            return transcript

        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
            return None
        except APIError as e:
            logger.error(f"Ошибка API OpenAI при транскрибации: {str(e)}", exc_info=True)
            raise  # Повторная попытка через декоратор retry
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при транскрибации: {str(e)}", exc_info=True)
            return None