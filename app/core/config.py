from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://svc_wallet:svc_wallet@db:5432/svc_wallet"
    SVC_USERS_URL: str = "http://host.docker.internal:9002"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_BALANCE_TTL: int = 43200  # 12 hours in seconds

    class Config:
        env_file = ".env"

settings = Settings()
