from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite+aiosqlite:///./frontdesk.db"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    request_timeout_hours: int = 24
    supervisor_webhook_url: str = ""
    sms_webhook_url: str = ""
    allowed_origins: str = "http://localhost:5173"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


settings = Settings()
