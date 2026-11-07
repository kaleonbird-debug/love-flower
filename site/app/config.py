import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные из .env, если он существует
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "database" / "love_flower.db"))
DEBUG = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
