import os

class Settings:
    PROJECT_NAME: str = "AI Refund Agent API"
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "dummy-key")
    OPENAI_BASE_URL: str = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL: str = os.environ.get("LLM_MODEL", "gpt-4o")

settings = Settings()
