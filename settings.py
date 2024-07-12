from pydantic import Field
from pydantic_settings import BaseSettings
from typing_extensions import Optional


class DatabaseSettings(BaseSettings):
    IP_ADDRESS: str
    IP_PORT: int = 5432
    NAME: str
    USER_NAME: str
    USER_PASSWORD: str
    MIN_CONNECTIONS: int
    MAX_CONNECTIONS: int
    MAX_INACTIVE_CONNECTION_LIFETIME: int = 3600

    class Config:
        env_prefix = "DB_"
        case_sensitive = False


class LoggingSettings(BaseSettings):
    LOGGING_LEVEL: Optional[str] = Field(default="info", title="Logging level")
    class Config:
        env_prefix = "LG_"
        case_sensitive = False


db_settings = DatabaseSettings()
log_settings = LoggingSettings()