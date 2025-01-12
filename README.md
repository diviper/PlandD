# 🌀 PlanD v0.4.2 - "Самый умный планировщик во всех измерениях, Морти!"

> "Планирование - это как наука, Морти! *burp* 90% боли и 10% результата!" - Рик Санчез

## 🧠 Что это за штука?

PlanD - это ИИ-планировщик задач, который:
- 🤖 Использует OpenAI для анализа твоих планов ("Умнее, чем Джерри... хотя это не сложно!")
- 📊 Учится на твоих паттернах ("Как Рик, только без алкоголизма!")
- 🎯 Даёт умные рекомендации ("Точнее, чем навигатор в жопе Морти!")
- 📱 Telegram интерфейс ("Проще, чем починить НЛО!")
- 🔄 Отслеживание прогресса ("Точнее, чем GPS в жопе Морти!")

## 🛠️ Как установить эту штуку?

*"Слушай внимательно! Установить это проще, чем собрать концентрированную тёмную материю!"*

1. **Клонируй репозиторий** (*"Как клонирование Морти, только с кодом!"*):
   ```bash
   git clone https://github.com/yourusername/PlanD.git
   cd PlanD
   ```

2. **Создай виртуальное окружение** (*"Это как карманное измерение для Python!"*):
   ```bash
   python -m venv .venv
   # Для тех, кто с Земли измерения C-137:
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Установи зависимости** (*"Важнее, чем сыворотка от крысиной чумы!"*):
   ```bash
   pip install -r requirements.txt
   ```

4. **Настрой переменные окружения** (*"Секретнее, чем рецепт сока из Мигу!"*):
   ```env
   BOT_TOKEN=токен_от_бота_в_телеграме
   OPENAI_API_KEY=ключ_от_openai
   DATABASE_PATH=путь_к_базе_данных
   LOG_LEVEL=уровень_логирования
   TASK_ANALYSIS_TEMPERATURE=0.7
   MAX_CACHE_SIZE=1000
   ```

5. **Запусти эту красоту** (*"Запускай, Морти! Запускай эту *burp* штуку!"*):
   ```bash
   python -m src.bot.__main__
   ```

## 🧪 О проекте

PlanD - это AI-powered планировщик задач, который помогает пользователям эффективно организовывать свои планы и достигать целей. Проект использует OpenAI GPT для анализа планов, обучения на паттернах пользователя и предоставления умных рекомендаций.

### 🌟 Основные возможности
- 🧠 AI анализ планов ("Умнее, чем Джерри в свой лучший день!")
- 📊 Машинное обучение на паттернах ("Как Рик, только без *burp* алкоголя!")
- 🎯 Умные рекомендации ("Лучше советов Мисикса!")
- 📱 Telegram интерфейс ("Проще, чем починить НЛО!")
- 🔄 Отслеживание прогресса ("Точнее, чем GPS в жопе Морти!")

## 🚀 Установка и запуск

1. Установка зависимостей:
```bash
pip install -r requirements.txt
```

2. Настройка окружения (.env):
```env
BOT_TOKEN=<telegram_token>
OPENAI_API_KEY=<openai_key>
DATABASE_PATH=tasks.db
LOG_LEVEL=DEBUG
TASK_ANALYSIS_TEMPERATURE=0.7
MAX_CACHE_SIZE=1000
```

3. Запуск бота:
```bash
python src/bot/main.py
```

## 📁 Структура проекта

### Критически важные компоненты (9-10/10)

#### Core Services
- **config.py (10/10)**: Центральная конфигурация системы
- **bot.py (9/10)**: Основная логика Telegram бота
- **database.py (9/10)**: Управление данными
- **models.py (9/10)**: Модели данных SQLAlchemy

#### AI Services
- **ai_service.py (9/10)**: Интеграция с OpenAI GPT
- **analyzer.py (9/10)**: Анализ задач и планов
- **planner.py (9/10)**: Оптимизация планов

### Важные компоненты (7-8/10)

#### Task Management
- **tasks.py (8/10)**: Обработка задач
- **scheduler.py (8/10)**: Планировщик напоминаний
- **notifier.py (8/10)**: Система уведомлений

#### Database
- **migrations/** (8/10): Управление схемой БД
- **init_database.py (7/10)**: Инициализация БД

## 🧪 Тестирование

```bash
pytest tests/
```

Основные тесты:
1. Интеграция с OpenAI API
2. Обработка задач и планов
3. Система напоминаний
4. Пользовательские настройки

## 📝 Дневник разработки

### 13.01.2025 01:08 - Обновление системы обработки сообщений 🤖

#### 🛠️ Выполненные изменения
- Исправлена проблема с кодировкой UTF-8 в логах
- Обновлена регистрация обработчиков для aiogram 3.x
- Улучшена обработка текстовых сообщений
- Добавлена поддержка FSM для управления планами
- Улучшены ответы в стиле Рика и Морти

#### 🎯 Следующие шаги
1. Добавить категории и теги для задач
2. Реализовать визуализацию прогресса
3. Добавить пользовательские настройки напоминаний
4. Расширить возможности AI анализа
5. Добавить поддержку повторяющихся задач

## 🔧 Рекомендации по разработке

### Работа с критическими компонентами
1. Создавать резервные копии перед изменениями
2. Тестировать изменения изолированно
3. Проверять все зависимые модули

### Обновление базы данных
1. Использовать миграции через alembic
2. Проверять совместимость моделей
3. Тестировать на тестовых данных

### AI компоненты
1. Следить за версиями OpenAI API
2. Тестировать на разных типах задач
3. Оптимизировать использование токенов

## 🎯 План оптимизации

### Приоритетные задачи
1. Оптимизация использования API
2. Улучшение системы кэширования
3. Расширение тестового покрытия

### Будущие улучшения
1. Интеграция с другими планировщиками
2. Расширение AI возможностей
3. Улучшение UI/UX бота

## 🚨 Известные проблемы

1. Циклические импорты
   - ✓ Решено созданием `base.py`
   - Требуется проверка всех импортов

2. Сервис напоминаний
   - Использует старую модель `Task`
   - Требуется обновление для новых моделей

3. База данных
   - Требуются миграции для новой структуры
   - Необходимо добавить индексы

## 🔒 Безопасность

### Текущие меры
- API ключи хранятся в `.env`
- Используется SQLAlchemy для безопасной работы с БД
- Логирование всех операций

### Требуемые улучшения
- Добавить rate limiting для OpenAI API
- Улучшить валидацию входных данных
- Добавить мониторинг безопасности

## 📦 Зависимости

```
aiogram==3.3.0
python-dotenv==1.0.0
openai==1.6.1
sqlalchemy==2.0.37
alembic==1.14.0
apscheduler==3.10.0
```

## 🔄 Git рабочий процесс

### Типы коммитов
- `feat:` - новый функционал
- `fix:` - исправление ошибок
- `docs:` - обновление документации
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - обслуживание проекта

### Полезные команды
```bash
# Текущий статус
git status

# Просмотр изменений
git diff

# Отмена изменений в файле
git checkout -- имя_файла

# Создание новой ветки
git checkout -b имя_ветки
```

## 📝 Внутренняя документация

### О проекте

PlanD - это AI-powered планировщик задач, который помогает пользователям эффективно организовывать свои планы и достигать целей. Проект использует OpenAI GPT для анализа планов, обучения на паттернах пользователя и предоставления умных рекомендаций.

### Ключевые особенности
- 🧠 AI анализ планов и разбивка на шаги
- 📊 Обучение на паттернах пользователя
- 🎯 Умные рекомендации по оптимизации
- 📱 Telegram интерфейс
- 🔄 Отслеживание прогресса

### Структура проекта

#### Ключевые компоненты

##### AI Service (`src/services/ai/ai_service.py`)

Сердце системы - AI сервис, который:
- Анализирует планы пользователей
- Изучает паттерны продуктивности
- Генерирует рекомендации
- Использует OpenAI GPT-3.5-turbo

Особенности реализации:
- Асинхронная работа с API
- Retry механизмы для надежности
- Структурированные JSON ответы
- Логирование всех операций

##### База данных (`src/database/`)

- `models.py`: SQLAlchemy модели
- `database.py`: Управление подключениями
- `base.py`: Базовый класс для моделей

Модели:
- Plan: Структура планов
- PlanStep: Шаги плана
- PlanProgress: Отслеживание прогресса
- UserPreferences: Настройки пользователя

##### Telegram Bot (`src/bot/`)

- Асинхронный бот на aiogram
- Интерактивные команды
- Умные напоминания

### Запуск проекта

1. Установка зависимостей:
```bash
pip install -r requirements.txt
```

2. Настройка окружения (.env):
```
BOT_TOKEN=<telegram_token>
OPENAI_API_KEY=<openai_key>
DATABASE_PATH=tasks.db
LOG_LEVEL=DEBUG
TASK_ANALYSIS_TEMPERATURE=0.7
MAX_CACHE_SIZE=1000
```

3. Запуск бота:
```bash
python src/bot/main.py
```

### Тестирование

Основной тестовый файл: `test_openai.py`
```bash
python test_openai.py
```

Тесты проверяют:
1. Анализ планов
2. Обучение на паттернах
3. Генерацию рекомендаций

### Рабочий процесс

#### Версионирование

- main: Стабильная версия
- v0.1: Первый релиз
- v0.4: Текущая версия (AI улучшения)

#### Ветки

- Используем feature branches для новых функций
- Версионные ветки для релизов
- Pull requests для code review

### Git команды
```bash
# Текущий статус
git status

# Просмотр изменений
git diff

# Отмена изменений в файле
git checkout -- имя_файла

# Создание новой ветки
git checkout -b имя_ветки
```

### Типы коммитов
- `feat:` - новый функционал
- `fix:` - исправление ошибок
- `docs:` - обновление документации
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - обслуживание проекта

### AI Особенности

#### Анализ планов

```json
{
  "title": "План изучения Python",
  "duration": "90 days",
  "steps": [
    "Основы программирования",
    "ООП",
    "Базы данных",
    "Веб-разработка"
  ]
}
```

#### Паттерны пользователя

```json
{
  "productivity_patterns": {
    "peak_hours": ["10:00-12:00"],
    "optimal_duration": "2 hours"
  },
  "recommendations": [
    "Планируйте сложные задачи на утро",
    "Используйте метод Помодоро"
  ]
}

## 📦 Что под капотом?

### Основные компоненты
- **config.py**: Центральная конфигурация ("Мозг операции!")
- **bot.py**: Логика Telegram бота ("Интерфейс для тупых... в смысле, для пользователей!")
- **ai_service.py**: ИИ сервис ("Умнее, чем вся Галактическая Федерация!")
- **database.py**: База данных ("Хранилище важнее, чем заначка Рика!")

### Зависимости
```
aiogram==3.3.0
python-dotenv==1.0.0
openai==1.6.1
sqlalchemy==2.0.37
alembic==1.14.0
apscheduler==3.10.0
```

## 🎯 Как использовать?

*"Это проще, чем управлять НЛО, Морти! Даже Джерри справится... наверное!"*

### Основные команды:
- `/start` - "Начать путешествие между измерениями!"
- `/help` - "Получить мудрость от Рика"
- `/plan` - "Создать новый гениальный план"
- `/stats` - "Узнать, насколько ты крут (или как Джерри)"

### Пример:
```
Ты: Надо подготовить презентацию к завтрашней встрече
Бот: *burp* Так, смотри сюда, Морти:

✅ Анализ задачи:
🎯 Приоритет: Высокий (важнее, чем прятать Мигу от Галактической Федерации)
⏰ Дедлайн: Завтра
⌛️ Длительность: 120 минут (это как 0.0001 микровселенной)

📋 План действий (простой, как азбука для Джерри):
1. Составить план презентации (30 мин)
2. Сделать слайды (60 мин)
3. Отрепетировать (30 мин)

💡 Совет от Рика: Начни с главного! И не тупи как Джерри!
```

## 🔮 Что нового в v0.4.2?

*"О-о-о, Морти, ты офигеешь от того, что мы добавили!"*

### Новые фичи
- ✨ Новый обработчик планов с улучшенным AI анализом
- 🚀 Оптимизированная структура AI сервисов
- 🔧 Улучшенная обработка ошибок

### Исправления
- 🐛 Исправлены циклические импорты
- 🔄 Оптимизирована работа с базой данных

### В разработке
- 📅 Улучшенная система напоминаний
- 🧠 Интеграция с GPT-4
- 💾 Векторное хранилище для кэширования

## 🤝 Вклад в проект

*"Хочешь помочь, Морти? Не облажайся!"*

1. Форкни репозиторий
2. Создай ветку для фичи (`git checkout -b feature/крутая-фича`)
3. Закоммить изменения (`git commit -am 'Добавил крутую фичу'`)
4. Пушни ветку (`git push origin feature/крутая-фича`)
5. Создай Pull Request

## 📄 Лицензия

*"Лицензия? Мораль это конструкт, Морти! Но юристы настаивают..."*

MIT License - делай что хочешь, только не забудь упомянуть автора!

## 🙏 Благодарности

*"Знаешь, Морти, даже гении иногда нуждаются в помощи..."*

- OpenAI за GPT
- Telegram за API
- Всем контрибьюторам за их вклад
- И конечно же, тебе, Морти!

---
