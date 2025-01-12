# PlanD - AI-Powered Planning Assistant

Personal AI assistant for planning and task management, powered by OpenAI.

## Version 0.4 Changes
- Complete AI service refactoring
  - Unified AI service for plan analysis and user patterns
  - Improved OpenAI integration with retry mechanisms
  - Better error handling and logging
- Database structure optimization
  - New models: Plan, PlanStep, PlanProgress, UserPreferences
  - Improved relationships between entities
  - Fixed circular dependencies
- Code quality improvements
  - Removed duplicate code
  - Better project structure
  - Enhanced testing coverage

## Features
- AI-powered plan analysis and structuring
- User pattern learning and optimization
- Progress tracking and analysis
- Telegram bot interface

## Installation
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create `.env` file with:
```
BOT_TOKEN=<your_telegram_bot_token>
OPENAI_API_KEY=<your_openai_api_key>
DATABASE_PATH=tasks.db
LOG_LEVEL=DEBUG
```

## Usage
Run the bot:
```bash
python src/bot/main.py
```

## Development
- Python 3.9+
- SQLAlchemy for database
- OpenAI API for AI features
- Aiogram for Telegram bot

## Testing
Run tests:
```bash
python test_openai.py
```

## License
MIT License
