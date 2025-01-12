"""Test OpenAI integration"""
import asyncio
import logging
from asyncio import TimeoutError

from src.services import AIService  # Обновленный импорт
from src.core.config import setup_logging
from src.database.database import Database
from src.database.models import UserPreferences

async def test_ai_service():
    setup_logging()
    db = Database()
    ai_service = AIService(db)
    
    # Создаем тестовые предпочтения пользователя
    session = db.get_session()
    try:
        # Сначала проверяем, существует ли запись
        existing_prefs = session.query(UserPreferences).filter_by(user_id=123).first()
        if existing_prefs:
            # Обновляем существующую запись
            existing_prefs.preferred_work_hours = "9:00-17:00"
            existing_prefs.peak_productivity_hours = "10:00-12:00"
            existing_prefs.typical_energy_curve = "High morning, low afternoon"
            existing_prefs.avg_task_completion_rate = 0.75
            existing_prefs.common_distractions = "['Social media', 'Email']"
        else:
            # Создаем новую запись
            test_prefs = UserPreferences(
                user_id=123,
                preferred_work_hours="9:00-17:00",
                peak_productivity_hours="10:00-12:00",
                typical_energy_curve="High morning, low afternoon",
                avg_task_completion_rate=0.75,
                common_distractions="['Social media', 'Email']"
            )
            session.add(test_prefs)
        session.commit()
    finally:
        session.close()
    
    # Тестовый план
    test_plan = "Хочу выучить Python за 3 месяца. Нужно освоить основы программирования, ООП, работу с базами данных и веб-разработку."
    
    print("Тестируем AI сервис...")
    try:
        # Анализ плана
        print("\n1. Анализ плана...")
        plan_data = await ai_service.analyze_plan(test_plan, "study")
        if plan_data:
            print("\nУспешный анализ плана:")
            print(f"Название: {plan_data['title']}")
            print(f"Длительность: {plan_data['estimated_duration']}")
            print(f"Приоритет: {plan_data['priority']}\n")
            print("Шаги:")
            for step in plan_data['steps']:
                print(f"- {step['title']} ({step['duration']})")
            print("\nРекомендации:")
            for rec in plan_data['recommendations'][:2]:
                print(f"- {rec}")
        else:
            print("Ошибка при анализе плана")

        # Анализ паттернов
        print("\n2. Анализ паттернов...")
        patterns = await ai_service.learn_patterns(123)
        if patterns:
            print("\nУспешный анализ паттернов:")
            print("Оптимальное время работы:", patterns['productivity_patterns']['peak_hours'])
            print("\nФакторы успеха:")
            for factor in patterns['success_factors'][:2]:
                print(f"- {factor}")
            print("\nРекомендации:")
            for rec in patterns['recommendations'][:2]:
                print(f"- {rec}")
        else:
            print("Ошибка при анализе паттернов")

    except TimeoutError:
        print("Ошибка: превышено время ожидания ответа от OpenAI")
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(test_ai_service())
    except KeyboardInterrupt:
        print("\nТест прерван пользователем")
    except Exception as e:
        print(f"Ошибка: {str(e)}")
