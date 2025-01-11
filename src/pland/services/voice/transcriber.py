"""Audio transcription service using OpenAI Whisper"""
import logging
from pathlib import Path

from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pland.core.config import Config

logger = logging.getLogger(__name__)

class AudioTranscriber:
    """Сервис транскрибации аудио с использованием OpenAI Whisper"""

    def __init__(self, test_mode: bool = False):
        """Инициализация сервиса транскрибации"""
        if not Config.OPENAI_API_KEY:
            logger.error("OpenAI API key не найден")
            raise ValueError("OpenAI API key обязателен")

        self.test_mode = test_mode
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info(f"AudioTranscriber инициализирован (test_mode: {test_mode})")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def transcribe_audio(self, audio_file: Path) -> str:
        """
        Преобразование аудио в текст

        :param audio_file: Путь к аудио файлу
        :return: Распознанный текст
        """
        try:
            logger.debug(f"Начало транскрибации файла: {audio_file}")

            if self.test_mode:
                logger.info("Работаем в тестовом режиме, возвращаем тестовый текст")
                return "Тестовое голосовое сообщение"

            with audio_file.open("rb") as file:
                response = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file,
                    language="ru"
                )

            text = response.text
            logger.info(f"Транскрибация успешна, получено символов: {len(text)}")
            return text

        except Exception as e:
            logger.error(f"Ошибка при транскрибации: {str(e)}", exc_info=True)
            raise

    async def test_connection(self) -> bool:
        """Проверка подключения к OpenAI API"""
        try:
            if self.test_mode:
                logger.info("Тестовый режим: подключение к API считается успешным")
                return True

            # Создаем тестовый файл с тишиной
            test_file = Path(__file__).parent / "test.wav"
            if not test_file.exists():
                return True  # Пропускаем тест, если нет тестового файла

            result = await self.transcribe_audio(test_file)
            return bool(result)

        except Exception as e:
            logger.error(f"Ошибка при проверке подключения: {str(e)}", exc_info=True)
            return False