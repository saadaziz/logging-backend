import os
from dotenv import load_dotenv

# Only load .env for local development — skip if already set in cPanel
if not os.getenv("JWT_SECRET_KEY"):
    load_dotenv()

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

def get_required_env(key):
    val = os.getenv(key)
    if DEV_MODE:
        return val
    if not val or val.startswith("<") or "secret" in val:
        raise Exception(f"{key} not set or still uses a placeholder!")
    return val

# ── JWT Config ────────────────────────────────────────────────────────────
JWT_SECRET_KEY = get_required_env("JWT_SECRET_KEY")
JWT_ISSUER = get_required_env("JWT_ISSUER")

# ── Logging Microservice API Key (optional for future use) ────────────────
SERVICE_KEY = os.getenv("JWT_SERVICE_KEY", "super-secret-key")

# ── Database ───────────────────────────────────────────────────────────────
DB_URL = os.getenv("LOG_DB_URL", "sqlite:///logs.db")
