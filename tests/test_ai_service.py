"""Test AI service functionality"""
import pytest
from datetime import datetime, timedelta
from src.services.ai.ai_service import AIService
from src.database.models_v2 import Plan, TimeBlock, Priority
from src.database.database import Database

@pytest.fixture
def ai_service():
    """AI service fixture"""
    return AIService()

@pytest.mark.asyncio
async def test_analyze_plan():
    """Test plan analysis"""
    ai_service = AIService()
    
    # Тест простого плана
    result = await ai_service.analyze_plan(
        "Позвонить маме вечером"
    )
    assert isinstance(result, dict)
    assert "title" in result
    assert "time_block" in result
    assert "priority" in result
    assert "steps" in result
    
    # Тест плана с шагами
    result = await ai_service.analyze_plan(
        """
        Подготовить презентацию
        - Собрать данные
        - Сделать слайды
        - Добавить анимацию
        """
    )
    assert len(result["steps"]) == 3
    assert all("duration" in step for step in result["steps"])

@pytest.mark.asyncio
async def test_determine_priority():
    """Test priority determination"""
    ai_service = AIService()
    
    # Высокий приоритет
    high_priority = await ai_service.determine_priority(
        "Срочная встреча с клиентом!!!"
    )
    assert high_priority == Priority.HIGH
    
    # Средний приоритет
    medium_priority = await ai_service.determine_priority(
        "Сходить в магазин за продуктами"
    )
    assert medium_priority == Priority.MEDIUM
    
    # Низкий приоритет
    low_priority = await ai_service.determine_priority(
        "Посмотреть новый сериал"
    )
    assert low_priority == Priority.LOW

@pytest.mark.asyncio
async def test_suggest_time_block():
    """Test time block suggestion"""
    ai_service = AIService()
    
    # Утренние дела
    morning = await ai_service.suggest_time_block(
        "Сходить на пробежку"
    )
    assert morning == TimeBlock.MORNING
    
    # Дневные дела
    afternoon = await ai_service.suggest_time_block(
        "Встреча с командой"
    )
    assert afternoon == TimeBlock.AFTERNOON
    
    # Вечерние дела
    evening = await ai_service.suggest_time_block(
        "Посмотреть фильм"
    )
    assert evening == TimeBlock.EVENING

@pytest.mark.asyncio
async def test_estimate_steps_duration():
    """Test steps duration estimation"""
    ai_service = AIService()
    
    steps = [
        "Собрать данные",
        "Сделать слайды",
        "Добавить анимацию"
    ]
    
    durations = await ai_service.estimate_steps_duration(steps)
    assert len(durations) == len(steps)
    assert all(isinstance(d, int) for d in durations)
    assert all(d > 0 for d in durations)

@pytest.mark.asyncio
async def test_generate_response():
    """Test response generation"""
    ai_service = AIService()
    
    # Проверяем баланс юмора
    response = await ai_service.generate_response(
        "Создан новый план",
        humor_level=0.2  # 20% юмора
    )
    
    # Должно содержать элементы стиля Рика
    assert any(phrase in response.lower() for phrase in ["морти", "*burp*", "🥒"])
    
    # Но не должно быть переполнено ими
    rick_phrases = sum(
        1 for phrase in ["морти", "*burp*", "🥒"] 
        if phrase in response.lower()
    )
    assert rick_phrases <= 2  # Не более 2 фраз в стиле Рика

@pytest.mark.asyncio
async def test_analyze_user_preferences():
    """Test user preferences analysis"""
    ai_service = AIService()
    
    # История планов пользователя
    plans = [
        "Утренняя пробежка",
        "Тренировка в зале",
        "Йога"
    ]
    
    preferences = await ai_service.analyze_user_preferences(plans)
    assert "interests" in preferences
    assert "preferred_time" in preferences
    assert "activity_level" in preferences
    
    # Должен определить интерес к спорту
    assert any("спорт" in interest.lower() for interest in preferences["interests"])
