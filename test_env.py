"""Test environment variables loading"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Get the absolute path to the .env file
env_path = Path(__file__).parent / '.env'
print(f"Looking for .env at: {env_path}")
print(f"File exists: {env_path.exists()}")

# Load environment variables
load_dotenv(env_path)

# Print environment variables
print("\nEnvironment variables:")
print(f"BOT_TOKEN: {os.getenv('BOT_TOKEN')}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
print(f"LOG_LEVEL: {os.getenv('LOG_LEVEL')}")

# Print all environment variables
print("\nAll environment variables:")
for key, value in os.environ.items():
    if key in ['BOT_TOKEN', 'OPENAI_API_KEY', 'LOG_LEVEL', 'DATABASE_PATH']:
        print(f"{key}: {value}")
