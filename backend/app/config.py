from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/paper_cut"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "paper-cut-cooperative-secret-key-2026"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"


settings = Settings()
