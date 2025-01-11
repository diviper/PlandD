# PlanD - AI-powered Telegram Bot для планирования задач

## 🌟 Возможности

### Основные функции
- 🤖 **AI-анализ задач**: Автоматическое понимание и структурирование задач с помощью OpenAI GPT-4o
- 📋 **Умная декомпозиция**: Разбивка сложных задач на подзадачи с оценкой времени и энергозатрат
- ⚡️ **Приоритизация**: Интеллектуальная система определения важности задач
- ⏰ **Гибкие напоминания**: Настраиваемая система уведомлений с учетом приоритетов
- 🎤 **Голосовой ввод**: Создание задач через голосовые сообщения
- 📊 **Энергетический профиль**: Учет оптимального времени и энергозатрат для каждой задачи
- 🔄 **Оптимизация**: Рекомендации по эффективному выполнению задач
- 📅 **Ежедневные сводки**: Автоматическое планирование дня

### AI функционал
- 🧠 **Контекстный анализ**: Глубокое понимание сути задач и их взаимосвязей
- ⚖️ **Оценка сложности**: Автоматическое определение сложности и требуемых ресурсов
- 🎯 **Умные рекомендации**: Контекстно-зависимые советы по выполнению задач
- 🔋 **Энергетический баланс**: Оптимизация распределения задач по энергозатратам

## 🚀 Быстрый старт

### Требования
- Python 3.11+
- Telegram Bot Token (получить у @BotFather)
- OpenAI API Key

### Установка
```bash
# Клонируем репозиторий
git clone https://github.com/yourusername/pland.git
cd pland

# Устанавливаем зависимости
python -m pip install -e .
```

### Настройка
Создайте файл `.env` с необходимыми переменными окружения:
```env
# Токены
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key

# Настройки логирования (опционально)
LOG_LEVEL=INFO
```

### Запуск
```bash
python -m src.pland.bot.__main__
```

## 💡 Использование

### Команды бота
- `/start` - Начало работы с ботом
- `/help` - Справка по командам
- `/add` - Создание новой задачи
- `/list` - Просмотр списка задач
- `/upcoming` - Ближайшие задачи
- `/done [ID]` - Отметить задачу выполненной
- `/delete [ID]` - Удалить задачу
- `/analyze` - Анализ текущих задач
- `/optimize` - Оптимизация расписания
- `/energy` - Рекомендации по энергии

### Примеры использования

#### Создание задачи через текст
```
Нужно подготовить презентацию к завтрашней встрече в 15:00
```
Бот автоматически:
- Определит приоритет и срок
- Разобьет на подзадачи
- Оценит необходимое время
- Предложит оптимальное расписание

#### Голосовые сообщения
1. Отправьте голосовое сообщение
2. Бот преобразует его в текст
3. Выполнит анализ и создаст задачу

## 🛠 Разработка

### Тесты
```bash
pytest tests/
```

### Линтинг
```bash
ruff check .
black .
```

## 🔒 Безопасность
- API ключи храните только в `.env`
- Используйте rate limiting для API
- Регулярно обновляйте зависимости

## 📄 Лицензия
MIT