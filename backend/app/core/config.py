from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    Values are read from environment variables / a .env file in backend/.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Security
    secret_key: str = "insecure-dev-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days

    # Database
    database_url: str = "sqlite:///./data/app.db"

    # Groq / LLM
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"

    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ML
    ml_min_training_events: int = 30

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
