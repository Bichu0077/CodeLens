from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://codelens:codelens_dev@localhost:5432/codelens"
    secret_key: str = "dev_secret_change_in_prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day
    groq_api_key: str = ""

    # Docker sandbox settings
    sandbox_image: str = "python:3.11-slim"
    sandbox_timeout: int = 10  # seconds before SIGKILL
    sandbox_mem_limit: str = "128m"
    sandbox_cpu_quota: int = 50000  # 50% of one CPU

    class Config:
        env_file = ".env"


settings = Settings()
