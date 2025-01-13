# Сценарии разработчика PlanD Bot

## 1. Разработка новой функциональности

### 1.1 Добавление новой команды бота

```python
# 1. Создание обработчика в src/bot/handlers/new_feature_handler.py
from aiogram import types
from aiogram.dispatcher import FSMContext
from src.core.states import NewFeatureStates
from src.database import Database
from src.services.ai import AIService

async def cmd_new_feature(message: types.Message, state: FSMContext, db: Database):
    """
    Обработчик новой команды
    """
    try:
        # Очистка предыдущего состояния
        await state.clear()
        
        # Установка нового состояния
        await state.set_state(NewFeatureStates.WAITING_FOR_INPUT)
        
        # Сохранение данных пользователя
        await state.update_data(user_id=message.from_user.id)
        
        # Отправка приветственного сообщения
        await message.answer(
            "Новая функция активирована, Морти!\n"
            "Расскажи, что ты хочешь сделать?"
        )
    except Exception as e:
        logger.error(f"Ошибка в cmd_new_feature: {e}")
        await message.answer("Произошла ошибка при запуске команды")
```

### 1.2 Интеграция с базой данных

```python
# 2. Создание модели в src/database/models/new_feature.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database.database import Base

class NewFeature(Base):
    __tablename__ = 'new_features'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON)
    status = Column(String)
    
    # Отношения
    user = relationship("User", back_populates="features")
```

### 1.3 Добавление AI-функциональности

```python
# 3. Расширение AI сервиса в src/services/ai/ai_service.py
async def analyze_new_feature(self, text: str) -> Dict:
    """Анализ новой функциональности с помощью AI"""
    messages = [
        {
            "role": "system",
            "content": """Анализ новой функции в стиле Рика.
            Верни JSON с полями:
            {
                "feature_type": "тип функции",
                "complexity": 1-10,
                "requirements": ["список требований"],
                "rick_comment": "комментарий от Рика"
            }"""
        },
        {"role": "user", "content": f"Функция: {text}"}
    ]
    
    return await self._get_completion(messages, {"type": "json_object"})
```

## 2. Сценарии тестирования

### 2.1 Модульные тесты

```python
# tests/test_handlers/test_new_feature.py
import pytest
from unittest.mock import AsyncMock, patch
from src.bot.handlers.new_feature_handler import cmd_new_feature

@pytest.mark.asyncio
async def test_cmd_new_feature():
    # Подготовка
    message = AsyncMock()
    state = AsyncMock()
    db = AsyncMock()
    
    # Выполнение
    await cmd_new_feature(message, state, db)
    
    # Проверка
    state.clear.assert_called_once()
    state.set_state.assert_called_once()
    message.answer.assert_called_once()
```

### 2.2 Интеграционные тесты

```python
# tests/test_integration/test_new_feature_flow.py
@pytest.mark.asyncio
async def test_new_feature_flow():
    # Подготовка системы
    bot = Bot(token=TEST_BOT_TOKEN)
    dp = Dispatcher()
    db = Database()
    
    # Симуляция действий пользователя
    message = types.Message(
        chat=types.Chat(id=123, type="private"),
        from_user=types.User(id=456, is_bot=False),
        text="/new_feature"
    )
    
    # Проверка полного flow
    response = await dp.message_handlers.notify(message)
    assert "Новая функция активирована" in response.text
```

## 3. Сценарии развертывания

### 3.1 Локальное развертывание

```bash
# 1. Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Установка зависимостей
pip install -r requirements.txt

# 3. Настройка переменных окружения
cp .env.example .env
# Редактируем .env файл

# 4. Инициализация базы данных
python -m src.database.init_db

# 5. Запуск бота
python -m src.bot
```

### 3.2 Docker развертывание

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "-m", "src.bot"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  bot:
    build: .
    env_file: .env
    volumes:
      - ./data:/app/data
    restart: always
```

## 4. Сценарии отладки

### 4.1 Логирование

```python
# src/core/logging.py
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    
    # Настройка логгеров компонентов
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
```

### 4.2 Отладка AI-компонента

```python
async def debug_ai_response(text: str):
    """Отладка ответов AI"""
    ai_service = AIService()
    
    # 1. Анализ текста
    text_analysis = await ai_service.analyze_text(text)
    print(f"Text Analysis:\n{json.dumps(text_analysis, indent=2)}")
    
    # 2. Анализ плана
    plan_analysis = await ai_service.analyze_plan(text)
    print(f"Plan Analysis:\n{json.dumps(plan_analysis, indent=2)}")
    
    # 3. Генерация ответа
    response = await ai_service.generate_response({
        "text_analysis": text_analysis,
        "plan_analysis": plan_analysis
    })
    print(f"Generated Response:\n{response}")
```

## 5. Сценарии оптимизации

### 5.1 Кэширование AI-ответов

```python
from functools import lru_cache
from typing import Dict, Any

class AICache:
    def __init__(self):
        self.cache = {}
        self.max_size = 1000
    
    @lru_cache(maxsize=1000)
    async def get_cached_response(self, query: str) -> Dict[str, Any]:
        """Получение кэшированного ответа"""
        cache_key = hash(query)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Если нет в кэше, получаем новый ответ
        response = await self.ai_service.get_response(query)
        self.cache[cache_key] = response
        return response
```

### 5.2 Оптимизация базы данных

```python
# src/database/optimizations.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

def optimize_sqlite():
    """Оптимизация SQLite"""
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=30000000000")
        cursor.close()
```

## 6. Сценарии мониторинга

### 6.1 Метрики производительности

```python
# src/services/monitoring/metrics.py
from prometheus_client import Counter, Histogram
import time

# Метрики
ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'Time spent processing AI requests'
)
ai_requests_total = Counter(
    'ai_requests_total',
    'Total number of AI requests'
)

# Использование
@ai_request_duration.time()
async def measure_ai_request():
    ai_requests_total.inc()
    start_time = time.time()
    result = await ai_service.process_request()
    duration = time.time() - start_time
    return result
```

### 6.2 Алерты

```python
# src/services/monitoring/alerts.py
async def check_system_health():
    """Проверка здоровья системы"""
    checks = {
        "database": check_db_connection(),
        "ai_service": check_ai_service(),
        "bot": check_bot_status()
    }
    
    for service, status in checks.items():
        if not status['healthy']:
            await send_alert(
                f"Service {service} is unhealthy: {status['message']}"
            )
```

## 7. Рекомендации по разработке

1. **Структура кода:**
   - Следуйте принципам SOLID
   - Используйте типизацию
   - Документируйте код

2. **Обработка ошибок:**
   - Всегда используйте try-except
   - Логируйте ошибки
   - Предоставляйте понятные сообщения пользователю

3. **Тестирование:**
   - Пишите тесты для новой функциональности
   - Используйте моки для внешних сервисов
   - Проверяйте граничные случаи

4. **Оптимизация:**
   - Профилируйте код
   - Используйте кэширование
   - Оптимизируйте запросы к базе данных

5. **Безопасность:**
   - Проверяйте входные данные
   - Используйте параметризованные запросы
   - Защищайте чувствительные данные

# PlanD Bot - Технический контекст

## Ключевые компоненты

### 1. AI Стиль (v0.6.1)
```python
# Текущая проблема: слишком много юмора, мало структуры
current_response = """
О, burp Морти, посмотри на этого парня...
[много юмора, мало конкретики]
"""

# Требуемый формат:
required_format = """
⏰ 09:00-10:30 | Подготовка
- Конкретное действие
- Конкретное действие
Приоритет: Высокий
"""
```

### 2. Структура планов
```python
class TimeStructuredPlan:
    def __init__(self):
        self.time_blocks = {
            'morning': [],    # 06:00-12:00
            'afternoon': [],  # 12:00-18:00
            'evening': []     # 18:00-23:00
        }
        self.deadlines = {}
        self.priorities = []
```

### 3. Критические проблемы
- ❌ Команда /plans не работает
- ❌ Нет временной структуры в планах
- ❌ Избыток юмора в ответах AI

### 4. База данных
```sql
-- Текущая структура
CREATE TABLE plans (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    content TEXT,
    created_at TIMESTAMP
);

-- Требуемые изменения
ALTER TABLE plans ADD COLUMN time_block TEXT;
ALTER TABLE plans ADD COLUMN priority TEXT;
ALTER TABLE plans ADD COLUMN deadline TIMESTAMP;
```

### 5. Промпты
```python
# Текущий промпт (проблемный)
CURRENT_PROMPT = """
Ты Рик из "Рика и Морти". Создай план...
[слишком общий]
"""

# Новый промпт (в разработке)
NEW_PROMPT = """
Ты Рик. Создай план со следующей структурой:
1. Временные блоки (утро/день/вечер)
2. Конкретные действия
3. Приоритеты
4. Дедлайны
Ограничь юмор 20% от ответа.
"""
```

## Текущие задачи

### 1. Исправление команды /plans
```python
@dp.message_handler(commands=['plans'])
async def cmd_plans(message: types.Message):
    # TODO:
    # 1. Добавить сортировку по времени
    # 2. Внедрить фильтры
    # 3. Исправить отображение
    pass
```

### 2. Структура временных блоков
```python
# Требуемый формат вывода
TIME_BLOCK_FORMAT = """
⏰ [Время] | [Название блока]
- [Действие 1]
- [Действие 2]
Приоритет: [Уровень]
Длительность: [Время]
"""
```

### 3. Метрики качества
```python
class QualityMetrics:
    def __init__(self):
        self.time_structure_rate = 0  # Целевое значение: 95%
        self.humor_ratio = 0          # Целевое значение: 20%
        self.plans_success_rate = 0   # Целевое значение: 98%
```

## Важные заметки

1. **Не коммитить:**
   - Файлы в директории docs/
   - Конфиденциальные данные
   - Временные файлы

2. **Версионность:**
   - Текущая версия: 0.6.1
   - Фокус на временной структуре
   - Баланс юмор/полезность

3. **API токены:**
   ```bash
   # Хранить в .env
   BOT_TOKEN=your_token
   OPENAI_API_KEY=your_key
   ```

## Быстрые команды

```bash
# Запуск бота
python -m src.bot

# Тесты
pytest tests/

# Миграции БД
python -m src.database.migrations

```

## 1. Работа с временной структурой

### 1.1 Создание плана с временными блоками

```python
# 1. Использование PlanServiceV2
from src.services.plan_service_v2 import PlanServiceV2
from src.database.models_v2 import TimeBlock, Priority

async def create_time_structured_plan(db: Session, user_id: int, data: dict):
    plan_service = PlanServiceV2(db)
    
    # Создание плана
    plan_data = {
        'title': 'Подготовка презентации',
        'time_block': TimeBlock.MORNING,
        'start_time': '09:00',
        'duration_minutes': 120,
        'priority': Priority.HIGH,
        'steps': [
            {
                'title': 'Сбор данных',
                'duration_minutes': 45,
                'priority': Priority.HIGH
            }
        ]
    }
    
    plan = plan_service.create_plan(user_id, plan_data)
    return plan
```

### 1.2 Обработка временных блоков

```python
# 2. Валидация времени в обработчике
@dp.message_handler(state=PlanStatesV2.WAITING_FOR_TIME)
async def process_time_input(message: types.Message, state: FSMContext):
    try:
        # Проверка формата времени
        start_time = datetime.strptime(message.text, '%H:%M').time()
        
        # Определение временного блока
        time_block = get_time_block(start_time)
        
        # Проверка доступности
        if not is_time_available(user_id, start_time):
            await message.answer("Это время уже занято!")
            return
            
        # Сохранение времени
        await state.update_data(start_time=start_time)
        
    except ValueError:
        await message.answer("Неверный формат времени! Используйте ЧЧ:ММ")
```

## 2. Интеграция с AI

### 2.1 Анализ плана через AIServiceV2

```python
# Использование улучшенного AI сервиса
from src.services.ai.ai_service_v2 import AIServiceV2

async def analyze_plan_with_time(plan_text: str, preferences: dict):
    ai_service = AIServiceV2()
    
    # Анализ плана с учетом времени
    plan_data = await ai_service.analyze_plan_v2(
        plan_text=plan_text,
        user_preferences=preferences
    )
    
    return plan_data
```

### 2.2 Форматирование ответов

```python
def format_plan_response(plan: Dict[str, Any]) -> str:
    """Форматирование плана для отображения"""
    return f"""
⏰ {plan['start_time']}-{plan['end_time']} | {plan['title']}
📝 {plan['description']}
🎯 Приоритет: {plan['priority'].value.capitalize()}
⏱ Длительность: {plan['duration_minutes']} минут

Шаги:
{''.join(f"- {step['title']} ({step['duration_minutes']} мин)\n" for step in plan['steps'])}
    """.strip()
```

## 3. Тестирование

### 3.1 Тесты временной структуры

```python
# test_time_structure.py
import pytest
from datetime import time
from src.database.models_v2 import TimeBlock

def test_time_block_detection():
    assert get_time_block(time(9, 0)) == TimeBlock.MORNING
    assert get_time_block(time(14, 0)) == TimeBlock.AFTERNOON
    assert get_time_block(time(19, 0)) == TimeBlock.EVENING

def test_duration_validation():
    with pytest.raises(ValueError):
        validate_duration(-30)
    with pytest.raises(ValueError):
        validate_duration(300)  # > 4 часа
```

### 3.2 Интеграционные тесты

```python
# test_integration.py
async def test_plan_creation_flow():
    # Создание плана
    plan_data = {
        'title': 'Test Plan',
        'time_block': 'morning',
        'start_time': '09:00',
        'duration_minutes': 60
    }
    
    # Проверка создания
    plan = await create_plan(plan_data)
    assert plan.time_block == TimeBlock.MORNING
    assert plan.duration_minutes == 60
    
    # Проверка конфликтов
    conflict = await check_time_conflicts(plan)
    assert not conflict
```

## 4. Миграция данных

### 4.1 Выполнение миграции

```bash
# Применение миграции
python -m alembic upgrade head

# Откат при необходимости
python -m alembic downgrade -1
```

### 4.2 Перенос данных

```python
# migrate_plans.py
async def migrate_plans():
    """Миграция старых планов в новый формат"""
    old_plans = await get_old_plans()
    
    for plan in old_plans:
        # Конвертация в новый формат
        new_plan = convert_to_new_format(plan)
        
        # Сохранение
        await save_new_plan(new_plan)
```

## 5. Мониторинг

### 5.1 Метрики времени

```python
class TimeMetrics:
    def __init__(self):
        self.time_block_usage = {
            'morning': 0,
            'afternoon': 0,
            'evening': 0
        }
        self.avg_duration = 0
        self.completion_rate = 0
    
    def track_plan(self, plan):
        """Отслеживание метрик плана"""
        self.time_block_usage[plan.time_block.value] += 1
        self.avg_duration = calculate_average_duration()
        self.completion_rate = calculate_completion_rate()
```

### 5.2 Отчеты

```python
async def generate_time_report(user_id: int) -> str:
    """Генерация отчета по временным метрикам"""
    metrics = await get_user_metrics(user_id)
    
    return f"""
📊 Отчет по использованию времени:

Утро: {metrics.time_block_usage['morning']} планов
День: {metrics.time_block_usage['afternoon']} планов
Вечер: {metrics.time_block_usage['evening']} планов

⏱ Средняя длительность: {metrics.avg_duration} минут
✅ Процент выполнения: {metrics.completion_rate}%
    """.strip()
