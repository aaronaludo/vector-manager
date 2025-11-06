from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg2://vector_user:vector_pass@localhost:5432/vector_db"
    )
    gemini_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
