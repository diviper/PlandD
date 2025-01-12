"""Test OpenAI integration"""
import asyncio
import logging
from asyncio import TimeoutError

from src.services import AIService  # Обновленный импорт
from src.core.config import setup_logging
from src.database.database import Database

async def test_ai_service():
    setup_logging()
    db = Database()
    ai_service = AIService(db)
    
    # Тестовый план
    test_plan = "Хочу выучить Python за 3 месяца. Нужно освоить основы программирования, ООП, работу с базами данных и веб-разработку."
    
    print("Тестируем AI сервис...")
    try:
        # Анализ плана
        print("\n1. Анализ плана...")
        plan_result = await asyncio.wait_for(
            ai_service.analyze_plan(test_plan, "study"),
            timeout=15.0
        )
        
        if plan_result:
            print("\nУспешный анализ плана:")
            print(f"Название: {plan_result.get('title')}")
            print(f"Длительность: {plan_result.get('estimated_duration')} дней")
            print(f"Приоритет: {plan_result.get('priority')}")
            print("\nШаги:")
            for step in plan_result.get('steps', []):
                print(f"- {step.get('title')} ({step.get('duration')} дней)")
            print("\nРекомендации:")
            for rec in plan_result.get('recommendations', []):
                print(f"- {rec}")
        else:
            print("Ошибка при анализе плана")
            
        # Тестируем анализ паттернов
        print("\n2. Анализ паттернов...")
        patterns = await asyncio.wait_for(
            ai_service.learn_patterns(123),  # тестовый user_id
            timeout=10.0
        )
        
        if patterns:
            print("\nПаттерны пользователя:")
            peak_hours = patterns.get('productivity_patterns', {}).get('peak_hours', [])
            print(f"Пиковые часы: {', '.join(peak_hours)}")
            print(f"Оптимальная длительность: {patterns.get('productivity_patterns', {}).get('optimal_duration')}")
            
            print("\nФакторы успеха:")
            for factor in patterns.get('success_factors', []):
                print(f"- {factor}")
        else:
            print("Ошибка при анализе паттернов")
            
    except TimeoutError:
        print("Превышено время ожидания ответа от OpenAI")
    except KeyboardInterrupt:
        print("\nТест остановлен пользователем")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        logging.exception("Ошибка при тестировании AI сервиса")

if __name__ == "__main__":
    try:
        asyncio.run(test_ai_service())
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем")
