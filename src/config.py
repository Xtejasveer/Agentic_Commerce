import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL:str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/agentic_commerce"
    )
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_mock_key")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET","mock_secret")
    RAZORPAY_WEBHOOK_SECRET="mock_webhook_secret"
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR","./chroma_db")

    OPENROUTER_API_KEY : str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")

    MCP_TRANSPORT :str = os.getenv("MCP_TRANSPORT", "stdio")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()