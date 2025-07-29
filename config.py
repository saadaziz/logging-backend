import os
from dotenv import load_dotenv

# Only load .env for local development — skip if variable exists (cPanel)
if not os.getenv("JWT_SERVICE_KEY"):
    load_dotenv()

# API key for logging microservice
SERVICE_KEY = os.getenv("JWT_SERVICE_KEY", "super-secret-key")

# Database URL (SQLite for now, MySQL later)
DB_URL = os.getenv("LOG_DB_URL", "sqlite:///logs.db")
