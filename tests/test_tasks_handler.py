"""Tests for task message handlers"""
import asyncio
import logging
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pland.bot.handlers.tasks import handle_text_message
from pland.database.database import Database

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_message():
    """Create mock message for tests"""
    message = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "test_user"
    message.text = "Нужно подготовить презентацию к завтрашней встрече в 15:00"
    # Мокаем метод answer
    message.answer = AsyncMock()
    return message

@pytest.fixture
def mock_db():
    """Create mock database for tests"""
    return MagicMock(spec=Database)

@pytest.mark.asyncio
async def test_handle_text_message(mock_message, mock_db):
    """Test text message processing"""
    # Выполняем тест
    await handle_text_message(mock_message, mock_db)

    # Проверяем, что сообщение обработано
    assert mock_message.answer.call_count == 2  # Одно для "Анализирую" и одно для результата
    
    # Проверяем содержимое первого сообщения
    first_call = mock_message.answer.call_args_list[0]
    assert "🤔 Анализирую сообщение..." in first_call[0][0]

    # Получаем последнее сообщение
    last_call = mock_message.answer.call_args_list[-1]
    final_message = last_call[0][0]
    
    # Проверяем, что в ответе есть основные поля анализа
    assert "✅ Анализ задачи" in final_message
    assert "🎯 Приоритет:" in final_message
    assert "⏰ Оптимальное время:" in final_message
    assert "⚡️ Требуемая энергия:" in final_message
    assert "📝 Подзадачи:" in final_message

@pytest.mark.asyncio
async def test_handle_empty_text_message(mock_message, mock_db):
    """Test handling empty text message"""
    # Убираем текст из сообщения
    mock_message.text = None
    
    # Выполняем тест
    await handle_text_message(mock_message, mock_db)
    
    # Проверяем сообщение об ошибке
    mock_message.answer.assert_called_once_with("Пожалуйста, отправьте текст для анализа.")

@pytest.mark.asyncio
async def test_handle_task_analysis_error(mock_message, mock_db):
    """Test handling task analysis error"""
    # Создаем мок для TaskAnalyzer, который вызывает ошибку
    with patch('pland.bot.handlers.tasks.TaskAnalyzer') as mock_analyzer:
        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.analyze_task = AsyncMock(return_value=None)
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Выполняем тест
        await handle_text_message(mock_message, mock_db)
        
        # Проверяем сообщение об ошибке
        error_message = mock_message.answer.call_args_list[-1][0][0]
        assert "🚫" in error_message
        assert "Не удалось проанализировать сообщение" in error_message

if __name__ == "__main__":
    asyncio.run(test_handle_text_message(MagicMock(), MagicMock()))
