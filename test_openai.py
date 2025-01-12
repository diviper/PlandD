"""Test OpenAI integration"""
import asyncio
import logging
from asyncio import TimeoutError
from src.services.ai import TaskAnalyzer
from src.core.config import setup_logging

async def test_openai():
    setup_logging()
    analyzer = TaskAnalyzer()
    
    # Тестовый текст задачи (короткий и простой)
    test_text = "Купить молоко"
    
    print("Отправляем запрос в OpenAI...")
    try:
        # Добавляем таймаут в 10 секунд
        result = await asyncio.wait_for(analyzer.analyze_task(test_text), timeout=10.0)
        
        if result:
            print("\nУспешный ответ от OpenAI:")
            print(f"Приоритет: {result.get('priority')}")
            print(f"Дедлайн: {result.get('deadline')}")
            print(f"Длительность: {result.get('duration')} минут")
            print("\nПодзадачи:")
            for subtask in result.get('subtasks', []):
                print(f"- {subtask.get('title')} ({subtask.get('duration')} минут)")
        else:
            print("Ошибка при получении ответа от OpenAI")
            
    except TimeoutError:
        print("Превышено время ожидания ответа от OpenAI (10 секунд)")
    except KeyboardInterrupt:
        print("\nТест остановлен пользователем")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(test_openai())
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем")
