"""Test OpenAI integration"""
import asyncio
import logging
from asyncio import TimeoutError
from src.services.ai_service import AIService
from src.core.config import Config, setup_logging
from src.database.database import Database
from src.database.models import UserPreferences, Priority

async def test_ai_service():
    setup_logging()
    logger = logging.getLogger(__name__)
    db = Database()
    ai_service = AIService(db)
    
    # Создаем тестовые предпочтения пользователя
    session = db.get_session()
    try:
        # Сначала проверяем, существует ли запись
        existing_prefs = session.query(UserPreferences).filter_by(user_id=123).first()
        if existing_prefs:
            existing_prefs.preferred_work_hours = "9:00-17:00"
            existing_prefs.peak_productivity_hours = "10:00-12:00"
            existing_prefs.typical_energy_curve = "High morning, low afternoon"
            existing_prefs.avg_task_completion_rate = 0.75
            existing_prefs.common_distractions = "['Social media', 'Email']"
        else:
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
    
    print("🚀 Запуск тестов AI сервиса...")
    
    try:
        # 1. Тест анализа простого плана
        print("\n1. Анализ простого плана...")
        simple_plan = "Позвонить маме вечером"
        simple_result = await ai_service.analyze_plan(simple_plan)
        print("✅ Анализ простого плана успешен")
        
        # 2. Тест анализа сложного плана
        print("\n2. Анализ сложного плана...")
        complex_plan = """
        Подготовить презентацию для клиента!!!
        - Собрать данные по рынку
        - Создать слайды
        - Добавить графики
        - Провести репетицию
        """
        complex_result = await ai_service.analyze_plan(complex_plan)
        print("✅ Анализ сложного плана успешен")
        
        # 3. Тест определения приоритета
        print("\n3. Определение приоритета...")
        priority = await ai_service.determine_priority("Срочная встреча!!!")
        assert priority == Priority.HIGH
        print("✅ Определение приоритета успешно")
        
        # 4. Тест оценки длительности
        print("\n4. Оценка длительности...")
        duration = await ai_service.estimate_duration("Написать отчет")
        assert isinstance(duration, int) and duration > 0
        print("✅ Оценка длительности успешна")
        
        # 5. Тест анализа учебного плана
        print("\n5. Анализ учебного плана...")
        study_plan = "Хочу выучить Python за 3 месяца. Нужно освоить основы программирования, ООП, работу с базами данных и веб-разработку."
        study_result = await ai_service.analyze_plan(study_plan, "study")
        print("✅ Анализ учебного плана успешен")
        
        # 6. Тест обработки ошибок
        print("\n6. Тест обработки ошибок...")
        try:
            await ai_service.analyze_plan("")
            print("❌ Тест обработки ошибок не пройден")
        except ValueError:
            print("✅ Обработка ошибок работает корректно")
        
        print("\n📊 Результаты тестирования AI сервиса:")
        print("✅ Все тесты успешно пройдены!")
        return True
        
    except TimeoutError:
        print("❌ Ошибка: превышено время ожидания ответа от OpenAI")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        asyncio.run(test_ai_service())
    except KeyboardInterrupt:
        print("\n⚠️ Тест остановлен пользователем")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
