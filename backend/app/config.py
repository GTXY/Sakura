from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    upload_dir: str = "uploads"
    base_url: str = "http://localhost:8000"


settings = Settings()
