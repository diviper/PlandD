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
                    "priority": {
                        "level": "high",
                        "reason": "Важная встреча завтра",
                        "urgency": "срочно",
                        "importance": "важно"
                    },
                    "schedule": {
                        "optimal_time": "morning",
                        "estimated_duration": 60,
                        "deadline": "2025-01-11 15:00",
                        "buffer_time": 30,
                        "subtasks": [
                            {
                                "title": "Собрать материалы",
                                "description": "Подготовить все необходимые данные",
                                "duration": 30,
                                "order": 1,
                                "dependencies": []
                            }
                        ]
                    },
                    "resources": {
                        "energy_required": 8,
                        "focus_level": "high",
                        "materials": ["презентация"],
                        "prerequisites": [],
                        "dependencies": [],
                        "risks": [],
                        "optimization_tips": []
                    }
                }'''
            )
        )
    ]

    with patch.object(task_analyzer.client.chat.completions, 'create', AsyncMock(return_value=mock_response)):
        result = await task_analyzer.analyze_task(test_text)

        # Basic structure checks
        assert isinstance(result, dict)
        assert "priority" in result
        assert "schedule" in result
        assert "resources" in result

        # Content checks
        assert result["priority"]["level"] == "high"
        assert result["schedule"]["estimated_duration"] == 60
        assert isinstance(result["schedule"]["deadline"], str)
        assert len(result["schedule"]["subtasks"]) == 1

@pytest.mark.asyncio
async def test_analyze_task_caching(task_analyzer):
    """Test that task analysis results are properly cached"""
    test_text = "Тестовая задача для проверки кэширования"
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='''{
                    "priority": {
                        "level": "medium",
                        "reason": "Тест",
                        "urgency": "не срочно",
                        "importance": "важно"
                    },
                    "schedule": {
                        "optimal_time": "morning",
                        "estimated_duration": 30,
                        "deadline": "2025-01-11 12:00",
                        "buffer_time": 15,
                        "subtasks": []
                    },
                    "resources": {
                        "energy_required": 5,
                        "focus_level": "medium",
                        "materials": [],
                        "prerequisites": [],
                        "dependencies": [],
                        "risks": [],
                        "optimization_tips": []
                    }
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

    # Create mock request
    mock_request = MagicMock()
    mock_request.method = "POST"
    mock_request.url = "https://api.openai.com/v1/chat/completions"
    mock_request.headers = {"Authorization": "Bearer ..."}
    mock_request.body = "..."

    # Create APIError with mock request
    mock_error = APIError(
        message="API Rate Limit Exceeded",
        request=mock_request,
        body={"error": {"message": "Rate limit exceeded", "type": "rate_limit_error"}}
    )

    with patch.object(task_analyzer.client.chat.completions, 'create', AsyncMock(side_effect=mock_error)):
        result = await task_analyzer.analyze_task("Test task")
        assert result is None

@pytest.mark.asyncio
async def test_cache_clearing(task_analyzer):
    """Test cache clearing functionality"""
    test_text = "Тестовая задача"
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='''{
                    "priority": {
                        "level": "medium",
                        "reason": "Тест",
                        "urgency": "не срочно",
                        "importance": "средне"
                    },
                    "schedule": {
                        "optimal_time": "morning",
                        "estimated_duration": 30,
                        "deadline": "2025-01-11 12:00",
                        "buffer_time": 15,
                        "subtasks": []
                    },
                    "resources": {
                        "energy_required": 5,
                        "focus_level": "medium",
                        "materials": [],
                        "prerequisites": [],
                        "dependencies": [],
                        "risks": [],
                        "optimization_tips": []
                    }
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