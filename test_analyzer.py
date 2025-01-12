"""Test TaskAnalyzer functionality"""
import asyncio
from pland.services.ai.analyzer import TaskAnalyzer

async def test_analyzer():
    analyzer = TaskAnalyzer(test_mode=True)  # Явно указываем тестовый режим
    task_text = "Нужно подготовить презентацию к завтрашней встрече в 15:00"

    print("Отправляю запрос к OpenAI...")
    result = await analyzer.analyze_task(task_text)
    print("\nРезультат анализа:")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_analyzer())