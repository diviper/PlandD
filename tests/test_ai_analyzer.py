"""Tests for AI task analyzer"""
import asyncio
import logging
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from pland.services.ai.analyzer import TaskAnalyzer
from pland.core.config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def task_analyzer():
    """Create TaskAnalyzer instance for tests"""
    return TaskAnalyzer()

@pytest.mark.asyncio
async def test_analyze_task(task_analyzer):
    """Test task analysis functionality"""
    test_text = "Подготовить презентацию к завтрашней встрече в 15:00"

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='''{
                    "title": "Подготовить презентацию",
                    "priority": "high",
                    "due_date": "2025-01-11 15:00",
                    "estimated_duration": 60,
                    "suggested_time_of_day": "утро",
                    "energy_level": 8,
                    "priority_reason": "Важная встреча завтра",
                    "tasks": [
                        {
                            "title": "Собрать материалы",
                            "description": "Подготовить все необходимые данные",
                            "priority": "high",
                            "estimated_duration": 30,
                            "energy_level": 7,
                            "energy_type": "mental",
                            "optimal_time": "morning"
                        },
                        {
                            "title": "Создать слайды",
                            "description": "Оформить презентацию",
                            "priority": "high",
                            "estimated_duration": 60,
                            "energy_level": 8,
                            "energy_type": "mental",
                            "optimal_time": "morning"
                        },
                        {
                            "title": "Подготовить речь",
                            "description": "Написать и отрепетировать выступление",
                            "priority": "high",
                            "estimated_duration": 45,
                            "energy_level": 9,
                            "energy_type": "mental",
                            "optimal_time": "afternoon"
                        }
                    ],
                    "suggested_order": [0, 1, 2],
                    "energy_distribution": {
                        "morning": [0, 1],
                        "afternoon": [2],
                        "evening": []
                    }
                }'''
            )
        )
    ]

    with patch.object(task_analyzer.client.chat.completions, 'create', AsyncMock(return_value=mock_response)):
        result = await task_analyzer.analyze_task(test_text)

        # Basic structure checks
        assert isinstance(result, dict)
        assert "title" in result
        assert "priority" in result
        assert "due_date" in result
        assert "tasks" in result
        assert isinstance(result["tasks"], list)

        # Content checks
        assert result["title"] == "Подготовить презентацию"
        assert result["priority"] == Config.PRIORITY_HIGH
        assert isinstance(result["due_date"], datetime)
        assert len(result["tasks"]) == 3

        # Task structure checks
        first_task = result["tasks"][0]
        assert "title" in first_task
        assert "description" in first_task
        assert "estimated_duration" in first_task
        assert isinstance(first_task["estimated_duration"], int)
        assert "energy_level" in first_task
        assert isinstance(first_task["energy_level"], int)

@pytest.mark.asyncio
async def test_analyze_task_caching(task_analyzer):
    """Test that task analysis results are properly cached"""
    test_text = "Тестовая задача для проверки кэширования"
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='''{
                    "title": "Тестовая задача",
                    "priority": "medium",
                    "due_date": "2025-01-11 12:00",
                    "estimated_duration": 30,
                    "suggested_time_of_day": "утро",
                    "energy_level": 5,
                    "priority_reason": "Тест",
                    "tasks": [
                        {
                            "title": "Подзадача 1",
                            "description": "Описание 1",
                            "priority": "medium",
                            "estimated_duration": 15,
                            "energy_level": 4,
                            "energy_type": "mental",
                            "optimal_time": "morning"
                        }
                    ]
                }'''
            )
        )
    ]

    create_mock = AsyncMock(return_value=mock_response)
    with patch.object(task_analyzer.client.chat.completions, 'create', create_mock):
        # First call - should get result from API
        result1 = await task_analyzer.analyze_task(test_text)
        # Second call - should get result from cache
        result2 = await task_analyzer.analyze_task(test_text)

        assert result1 == result2
        create_mock.assert_called_once()  # API should be called only once

@pytest.mark.asyncio
async def test_api_error_handling(task_analyzer):
    """Test error handling for API calls"""
    from openai import APIError

    # Создаем mock объект для request
    mock_request = MagicMock()
    mock_request.method = "POST"
    mock_request.url = "https://api.openai.com/v1/chat/completions"
    mock_request.headers = {"Authorization": "Bearer ..."}
    mock_request.body = "..."

    # Создаем APIError с mock объектом request и body
    mock_error = APIError(
        message="API Error",
        request=mock_request,
        body={"error": {"message": "API Error", "type": "invalid_request_error"}}
    )

    with patch.object(task_analyzer.client.chat.completions, 'create', AsyncMock(side_effect=mock_error)):
        with pytest.raises(Exception) as exc_info:
            await task_analyzer.analyze_task("Test task")
        assert "API" in str(exc_info.value)

@pytest.mark.asyncio
async def test_due_date_parsing(task_analyzer):
    """Test parsing of different date formats"""
    # Test valid format
    valid_date = "2025-01-11 15:00"
    parsed_date = task_analyzer._parse_due_date(valid_date)
    assert isinstance(parsed_date, datetime)
    assert parsed_date.year == 2025
    assert parsed_date.month == 1
    assert parsed_date.day == 11
    assert parsed_date.hour == 15
    assert parsed_date.minute == 0

    # Test invalid format
    invalid_date = "2025/01/11"
    default_date = task_analyzer._parse_due_date(invalid_date)
    assert isinstance(default_date, datetime)
    time_diff = default_date - datetime.now()
    assert 0 < time_diff.total_seconds() < 86400 * 2  # Should be less than 2 days

@pytest.mark.asyncio
async def test_priority_mapping(task_analyzer):
    """Test priority mapping functionality"""
    assert task_analyzer._map_priority("high") == Config.PRIORITY_HIGH
    assert task_analyzer._map_priority("medium") == Config.PRIORITY_MEDIUM
    assert task_analyzer._map_priority("low") == Config.PRIORITY_LOW
    assert task_analyzer._map_priority("invalid") == Config.PRIORITY_MEDIUM

@pytest.mark.asyncio
async def test_cache_clearing(task_analyzer):
    """Test cache clearing functionality"""
    test_text = "Тестовая задача"
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='''{
                    "title": "Тест",
                    "priority": "medium",
                    "due_date": "2025-01-11 12:00",
                    "estimated_duration": 30,
                    "suggested_time_of_day": "утро",
                    "energy_level": 5,
                    "priority_reason": "Тест",
                    "tasks": []
                }'''
            )
        )
    ]

    create_mock = AsyncMock(return_value=mock_response)
    with patch.object(task_analyzer.client.chat.completions, 'create', create_mock):
        await task_analyzer.analyze_task(test_text)
        task_analyzer.clear_cache()
        await task_analyzer.analyze_task(test_text)
        assert create_mock.call_count == 2  # API should be called twice after cache clear

if __name__ == "__main__":
    asyncio.run(test_analyze_task(TaskAnalyzer()))