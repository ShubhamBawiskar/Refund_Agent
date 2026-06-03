import os

class Settings:
    PROJECT_NAME: str = "AI Refund Agent API"
    API_KEY: str = os.environ.get("API_KEY", "dummy-key")
    BASE_URL: str = os.environ.get("BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL: str = os.environ.get("LLM_MODEL", "gpt-4o")

settings = Settings()
