from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://svc_wallet:svc_wallet@db:5432/svc_wallet"
    SVC_USERS_URL: str = "http://host.docker.internal:9002"

    class Config:
        env_file = ".env"

settings = Settings()
