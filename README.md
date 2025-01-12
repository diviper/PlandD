# PlanD - AI-Powered Task Planner Bot

PlanD is a Telegram bot that helps you analyze and plan your tasks using OpenAI's GPT model. It breaks down complex tasks into manageable subtasks and helps you stay organized.

## Features

- 🤖 Task Analysis with OpenAI
- 📋 Automatic Task Breakdown
- ⏰ Smart Deadline Management
- 🔔 Task Reminders
- 📊 Priority Management
- 💾 Task History

## Project Structure

```
PlandD/
├── src/
│   ├── bot/                 # Telegram bot implementation
│   │   ├── handlers/       # Message handlers
│   │   └── bot.py         # Bot initialization
│   ├── services/           # Business logic
│   │   ├── ai/            # AI services (OpenAI integration)
│   │   └── reminder/      # Reminder services
│   ├── database/          # Database models and operations
│   └── core/              # Core configurations
└── requirements.txt       # Project dependencies
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PlandD.git
cd PlandD
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
LOG_LEVEL=DEBUG
DATABASE_PATH=tasks.db
```

4. Run the bot:
```bash
python -m src.bot
```

## Usage

1. Start the bot by sending `/start`
2. Send any task description, for example:
   "Need to prepare a presentation for tomorrow's meeting"
3. The bot will analyze your task and:
   - Set priority
   - Suggest deadline
   - Break it down into subtasks
   - Calculate duration
4. Tasks are saved and you'll receive reminders

## Dependencies

- aiogram>=3.3.0
- python-dotenv>=1.0.0
- openai>=1.0.0
- sqlalchemy>=2.0.37
- alembic>=1.14.0
- apscheduler>=3.10.0

## Contributing

Feel free to open issues and submit pull requests.

## License

MIT License