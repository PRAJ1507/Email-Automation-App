from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost:5432/email_app"
    SENDGRID_API_KEY: str
    SENDGRID_FROM_EMAIL: str
    GROQ_API_KEY: str

    # Groq config
    GROQ_MODEL_NAME: str = "llama-3.1-8b-instant"
    GROQ_MAX_CALLS_PER_MIN: int = 30  # soft limit

    # Email sender name
    SENDER_FIRST_NAME: str = "Alex"

    # Single-user label
    APP_OWNER: str = "default_user"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
