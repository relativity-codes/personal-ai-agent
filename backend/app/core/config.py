from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str = "Personal AI Agent"
    DEBUG: bool = False

    class Config:
        env_file = "../../.env"   # points to root .env

settings = Settings()