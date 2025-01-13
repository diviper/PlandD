# Общее саммари проекта PlanD Bot (v0.5)

### Обзор проекта
PlanD Bot - это Telegram бот для планирования задач с элементами искусственного интеллекта, стилизованный под персонажа Рика из "Рика и Морти". Бот помогает пользователям создавать, анализировать и отслеживать выполнение планов и задач с юмористическим подходом.

### Ключевые особенности
1. **AI-Powered Планирование:**
   - Анализ планов с помощью GPT-4
   - Разбивка на конкретные шаги
   - Оценка длительности и приоритетов
   - Рекомендации по улучшению

2. **Уникальный стиль:**
   - Коммуникация в стиле Рика из "Рика и Морти"
   - Научный юмор и отсылки к сериалу
   - Саркастичные комментарии и советы

3. **Управление задачами:**
   - Создание и отслеживание планов
   - Система напоминаний
   - Приоритизация задач
   - Оценка рисков и сложности

### Технический стек
- **Backend:** Python 3.11+
- **Framework:** aiogram 3.x
- **AI:** OpenAI GPT-4
- **Database:** SQLite + SQLAlchemy
- **Deployment:** Docker (планируется)

### История разработки

#### Версия 0.1-0.3 (Начальная разработка)
- Базовая структура проекта
- Интеграция с Telegram API
- Простые команды и обработчики
- Базовая работа с базой данных

#### Версия 0.4 (AI Integration)
- Интеграция с OpenAI API
- Базовый анализ планов
- Система промптов
- Обработка естественного языка

#### Версия 0.5 (Текущая)
- Улучшенный AI анализ
- Интерактивное планирование
- Система кэширования
- Оптимизация производительности

### Процесс работы с пользователем

#### Основные сценарии использования
1. **Создание плана:**
   ```
   User: /plan
   Bot: "Отлично, Морти! Расскажи о своем плане"
   User: [описание плана]
   Bot: [AI анализ и разбивка на шаги]
   ```

2. **Просмотр планов:**
   ```
   User: /plans
   Bot: [список активных планов]
   ```

3. **Управление напоминаниями:**
   ```
   User: /remind [время]
   Bot: [установка напоминания]
   ```

#### Особенности взаимодействия
- Юмористический тон общения
- Научные термины и отсылки
- Адаптивные ответы на основе контекста
- Интерактивные кнопки и меню

### Текущие проблемы и вызовы
1. **Производительность:**
   - Долгое время ответа AI (15-20 сек)
   - Необходимость оптимизации запросов
   - Проблемы с кэшированием

2. **Пользовательский опыт:**
   - Отсутствие индикации загрузки
   - Проблемы с кнопками
   - Ограниченная интерактивность

3. **Технические ограничения:**
   - Ограничения API OpenAI
   - Проблемы с состояниями FSM
   - Необходимость улучшения базы данных

### План развития

#### Краткосрочные цели
- Исправление проблем с кнопками
- Оптимизация времени отклика
- Улучшение интерактивности планов

#### Среднесрочные цели
- Добавление аналитики использования
- Улучшение системы напоминаний
- Расширение функционала планирования

#### Долгосрочные цели
- Внедрение машинного обучения
- Персонализация рекомендаций
- Интеграция с календарями

### Заключение
PlanD Bot успешно развивается как уникальный инструмент планирования, сочетающий мощь AI с юмористическим подходом. Несмотря на текущие проблемы, проект имеет четкий план развития и активно совершенствуется на основе обратной связи от пользователей.

# Дневник разработки PlanD Bot - Часть 2

## 2025-01-13

### Выявленные проблемы

1. **Медленное время отклика AI сервиса:**
   - OpenAI API вызовы занимают 15-20 секунд каждый
   - Требуется оптимизация количества токенов и кэширование
   - Предложенные изменения:
     ```python
     - Добавление системы кэширования ответов
     - Уменьшение MAX_TOKENS до 800
     - Оптимизация промптов
     - Улучшенная обработка ошибок
     ```

2. **Проблемы с кнопками в планах:**
   - Кнопки "Погнали" и "Изменить" не реагируют на нажатия
   - Необходимо проверить обработчики callback_query
   - Возможные причины:
     - Неправильная структура callback_data
     - Отсутствие соответствующих обработчиков
     - Проблемы с состояниями FSM

3. **Отсутствие интерактивности при составлении плана:**
   - AI не реагирует на дополнения к плану
   - Нет возможности модифицировать план в процессе
   - Требуется:
     - Добавить состояние редактирования плана
     - Сохранять промежуточные версии плана
     - Обновлять анализ при каждом дополнении

### План улучшений

#### 1. Оптимизация AI сервиса
- [ ] Внедрить систему кэширования ответов
- [ ] Оптимизировать промпты для уменьшения токенов
- [ ] Добавить таймауты и retry логику
- [ ] Улучшить логирование для отладки

#### 2. Исправление кнопок плана
- [ ] Добавить логирование для callback_query
- [ ] Проверить структуру callback_data
- [ ] Обновить обработчики callback_query
- [ ] Добавить FSM состояния для редактирования

#### 3. Интерактивное планирование
- [ ] Добавить новое состояние FSM для редактирования плана
- [ ] Создать хранилище промежуточных версий плана
- [ ] Реализовать инкрементальный анализ дополнений
- [ ] Добавить кнопки для:
  - Добавления шагов
  - Изменения существующих шагов
  - Удаления шагов
  - Изменения порядка шагов

### Технические заметки

#### Структура callback_data
```python
# Текущая структура
callback_data = f"accept_plan:{plan_id}"

# Новая структура
callback_data = {
    "action": "plan",
    "operation": "accept|edit|add_step|remove_step",
    "plan_id": plan_id,
    "step_id": step_id  # опционально
}
```

#### FSM состояния для планов
```python
class PlanStates(StatesGroup):
    WAITING_FOR_PLAN = State()
    EDITING_PLAN = State()
    ADDING_STEP = State()
    CONFIRMING_CHANGES = State()
```

#### Хранение промежуточных версий
```python
class PlanVersion:
    plan_id: int
    version: int
    steps: List[PlanStep]
    created_at: datetime
    modified_by: str  # user/ai
```

### Следующие шаги

1. Начать с исправления кнопок, так как это блокирует базовую функциональность
2. Реализовать хранение версий плана для поддержки редактирования
3. Добавить интерактивное редактирование плана
4. Оптимизировать AI сервис для улучшения времени отклика

### Ожидаемые результаты

- Уменьшение времени отклика AI до 5-7 секунд
- Работающие кнопки управления планом
- Возможность интерактивного редактирования плана
- Улучшенный UX при составлении планов