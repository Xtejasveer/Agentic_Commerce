import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings:
    _raw_db_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/agentic_commerce"
    )
    # Railway and Heroku provide postgres:// which SQLAlchemy 1.4+ rejects in favor of postgresql://
    DATABASE_URL: str = (
        _raw_db_url.replace("postgres://", "postgresql://", 1)
        if _raw_db_url.startswith("postgres://")
        else _raw_db_url
    )
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_mock_key")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET","mock_secret")
    RAZORPAY_WEBHOOK_SECRET="mock_webhook_secret"
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR","./chroma_db")

    OPENROUTER_API_KEY : str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    MCP_TRANSPORT :str = os.getenv("MCP_TRANSPORT", "stdio")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()