# Структура проекта PlanD Bot

## 📁 Общая структура

```
PlandD/
├── 📁 src/                      # Исходный код
│   ├── 📁 bot/                 # Telegram бот
│   │   ├── handlers/          # Обработчики команд
│   │   └── states.py          # Состояния FSM
│   ├── 📁 database/           # База данных
│   │   ├── models_v2.py      # Модели данных
│   │   └── migrations/       # Миграции
│   └── 📁 services/           # Бизнес-логика
│       ├── ai/               # AI сервисы
│       └── plan/            # Работа с планами
├── 📁 tests/                   # Тесты
├── 📁 docs/                    # Документация
└── 📁 config/                  # Конфигурация
```

## 🤖 Telegram Bot (src/bot/)

### Обработчики (handlers/)
- `plan_handler_v2.py` - Создание планов
  ```python
  @dp.message_handler(commands=['plan'])
  async def cmd_plan(message: types.Message):
      """Начало создания плана"""
  
  @dp.message_handler(state=PlanStates.WAITING_FOR_TIME)
  async def process_time(message: types.Message):
      """Обработка времени"""
  ```

### Состояния (states.py)
```python
class PlanStatesV2(StatesGroup):
    WAITING_FOR_DESCRIPTION = State()
    WAITING_FOR_TIME = State()
    WAITING_FOR_CONFIRMATION = State()
```

## 📊 База данных (src/database/)

### Модели (models_v2.py)
```python
class Plan(Base):
    """План с временной структурой"""
    time_block = Column(Enum(TimeBlock))
    start_time = Column(Time)
    duration_minutes = Column(Integer)

class PlanStep(Base):
    """Шаг плана"""
    duration_minutes = Column(Integer)
    order = Column(Integer)
```

### Миграции (migrations/)
```bash
# Создание миграции
alembic revision -m "add_time_structure"

# Применение
alembic upgrade head
```

## 🧠 Сервисы (src/services/)

### AI (ai/)
- `ai_service_v2.py` - Анализ планов
  ```python
  class AIServiceV2:
      async def analyze_plan(self, text: str):
          """Анализ плана с временной структурой"""
  ```

### План (plan/)
- `plan_service_v2.py` - Управление планами
  ```python
  class PlanServiceV2:
      async def create_plan(self, data: dict):
          """Создание плана"""
      
      async def validate_time(self, time: str):
          """Проверка времени"""
  ```

## 🧪 Тесты (tests/)

### Unit Tests
```python
def test_time_validation():
    """Проверка валидации времени"""
    assert is_valid_time("09:00")

def test_plan_creation():
    """Проверка создания плана"""
    plan = create_plan(data)
    assert plan.time_block
```

### Integration Tests
```python
async def test_plan_flow():
    """Проверка полного процесса"""
    response = await bot.send_message("/plan")
    assert "Выберите время" in response
```

## ⚙️ Конфигурация (config/)

### config.py
```python
class Config:
    """Настройки бота"""
    TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    
    # Временные блоки
    TIME_BLOCKS = {
        "morning": (6, 12),
        "afternoon": (12, 18),
        "evening": (18, 23)
    }
```

## 📝 Документация (docs/)

- `README.internal.md` - Внутренняя документация
- `developer_scenarios.md` - Сценарии разработки
- `project_structure.md` - Структура проекта (этот файл)
- `project_map.json` - Карта проекта в JSON

## 🔄 Процесс разработки

1. **Создание фичи**
   ```bash
   git checkout -b feature/name
   # Разработка
   git commit -m "feat: description"
   ```

2. **Тестирование**
   ```bash
   pytest tests/
   ```

3. **Миграции**
   ```bash
   alembic upgrade head
   ```

## 📚 Гайды по разработке

### 1. Добавление новой команды

1. Создайте обработчик в `handlers/`:
   ```python
   @dp.message_handler(commands=['new_command'])
   async def cmd_new(message: types.Message):
       await message.answer("Response")
   ```

2. Добавьте состояния в `states.py`:
   ```python
   class NewStates(StatesGroup):
       WAITING = State()
   ```

3. Создайте тесты в `tests/`:
   ```python
   def test_new_command():
       assert handler_response == "Response"
   ```

### 2. Изменение базы данных

1. Обновите модели в `models_v2.py`:
   ```python
   class NewModel(Base):
       id = Column(Integer, primary_key=True)
   ```

2. Создайте миграцию:
   ```bash
   alembic revision -m "add_new_model"
   ```

3. Обновите тесты

### 3. Работа с AI

1. Добавьте новый метод в `ai_service_v2.py`:
   ```python
   async def new_analysis(self, text: str):
       """Новый тип анализа"""
   ```

2. Обновите промпты в `prompts/`
3. Добавьте тесты

## 🎯 Best Practices

1. **Код**
   - Type hints везде
   - Docstrings для методов
   - Black для форматирования

2. **Git**
   - Атомарные коммиты
   - Понятные сообщения
   - Pull requests

3. **Тесты**
   - Unit tests для логики
   - Integration tests для потоков
   - Mock для внешних сервисов
