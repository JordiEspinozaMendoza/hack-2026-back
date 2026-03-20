from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True
    APP_NAME: str = "FastAPI Template"

    class Config:
        env_file = ".env"


settings = Settings()
