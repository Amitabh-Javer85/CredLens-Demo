from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore"
    )

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    
    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Anthropic API (optional: fallback to canned memo if not configured)
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = ""  # Explicitly select a model when enabling live generation.
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


settings = Settings()
