"""Tests for voice message handler"""
import asyncio
import logging
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from aiogram import Bot
from pland.services.voice.handler import VoiceHandler

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_bot():
    """Create mock bot for tests"""
    bot = MagicMock(spec=Bot)
    bot.get_file = AsyncMock()
    bot.download_file = AsyncMock()
    return bot

@pytest.fixture
def voice_handler(mock_bot):
    """Create VoiceHandler instance for tests"""
    return VoiceHandler(mock_bot, test_mode=True)  # Включаем тестовый режим

@pytest.mark.asyncio
async def test_process_voice_message(voice_handler, mock_bot):
    """Test voice message processing"""
    # Создаем мок голосового сообщения
    voice = MagicMock()
    voice.file_id = "test_file_id"

    message = MagicMock()
    message.voice = voice

    # Настраиваем поведение мока бота
    mock_file = MagicMock()
    mock_file.file_path = "test_path"
    mock_bot.get_file.return_value = mock_file

    # Создаем временный тестовый файл
    temp_file = voice_handler.temp_dir / "test_file_id.ogg"
    temp_file.touch()

    # Имитируем загрузку файла
    async def mock_download(file_path, dest):
        with open(dest, 'wb') as f:
            f.write(b'test audio content')
    mock_bot.download_file.side_effect = mock_download

    # Выполняем тест
    result = await voice_handler.process_voice_message(message)

    # Проверяем результаты
    assert result == "Тестовое голосовое сообщение"
    mock_bot.get_file.assert_called_once_with("test_file_id")
    mock_bot.download_file.assert_called_once()

@pytest.mark.asyncio
async def test_error_handling(voice_handler, mock_bot):
    """Test error handling in voice processing"""
    message = MagicMock()
    message.voice = None

    result = await voice_handler.process_voice_message(message)
    assert result is None

@pytest.mark.asyncio
async def test_cleanup(voice_handler):
    """Test cleanup functionality"""
    # Создаем временный файл
    temp_file = voice_handler.temp_dir / "test.ogg"
    temp_file.touch()

    assert temp_file.exists()
    await voice_handler.cleanup()
    assert not temp_file.exists()

if __name__ == "__main__":
    asyncio.run(test_process_voice_message(VoiceHandler(Bot(token="test"), test_mode=True)))