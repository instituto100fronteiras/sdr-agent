
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Evolution API Credentials
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "Ivair")

# Chatwoot Credentials
CHATWOOT_API_URL = os.getenv("CHATWOOT_API_URL")
CHATWOOT_API_TOKEN = os.getenv("CHATWOOT_API_TOKEN")
CHATWOOT_ACCOUNT_ID = os.getenv("CHATWOOT_ACCOUNT_ID")
CHATWOOT_INBOX_ID = os.getenv("CHATWOOT_INBOX_ID")

# Trello Credentials
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD_ID = os.getenv("TRELLO_BOARD_ID")
TRELLO_LIST_COLD = os.getenv("TRELLO_LIST_COLD")
TRELLO_LIST_CONNECTION = os.getenv("TRELLO_LIST_CONNECTION")
TRELLO_LIST_INTERESTED = os.getenv("TRELLO_LIST_INTERESTED")
TRELLO_LIST_ARCHIVED = os.getenv("TRELLO_LIST_ARCHIVED")

# OpenAI Credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# SerpAPI Credentials
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Operational Settings
TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Working Hours (24h format)
WORK_HOURS_MORNING_START = "09:00"
WORK_HOURS_MORNING_END = "11:20"
WORK_HOURS_AFTERNOON_START = "14:00"
WORK_HOURS_AFTERNOON_END = "17:20"

# Warm-up Settings
WARMUP_ENABLED = os.getenv("WARMUP_ENABLED", "False").lower() == "true"
WARMUP_START_DATE = os.getenv("WARMUP_START_DATE") # Format: YYYY-MM-DD

# Scheduling
MESSAGE_INTERVAL_MINUTES = int(os.getenv("MESSAGE_INTERVAL_MINUTES", 30))

# Webhook Settings
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 5000))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# Validation
def validate_settings():
    required_vars = [
        "SUPABASE_URL", "SUPABASE_KEY",
        "EVOLUTION_API_URL", "EVOLUTION_API_KEY",
        "CHATWOOT_API_URL", "CHATWOOT_API_TOKEN", "CHATWOOT_ACCOUNT_ID"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

if __name__ == "__main__":
    try:
        validate_settings()
        print("Settings loaded successfully.")
    except ValueError as e:
        print(f"Configuration Error: {e}")
