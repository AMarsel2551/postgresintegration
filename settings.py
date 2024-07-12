from pydantic import Field
from pydantic_settings import BaseSettings
from typing_extensions import Optional


class DatabaseSettings(BaseSettings):
    IP_ADDRESS: str = Field(..., title="Ip address database")
    IP_PORT: int = Field(default=5432, title="Port address database")
    NAME: str = Field(..., title="Name address database")
    USER_NAME: str = Field(..., title="User name")
    USER_PASSWORD: str = Field(..., title="User password")

    class Config:
        env_prefix = "DB_"
        case_sensitive = False


class LoggingSettings(BaseSettings):
    LOGGING_LEVEL: Optional[str] = Field(default="debug", title="Logging level")

    class Config:
        env_prefix = "LG_"
        case_sensitive = False


db_settings = DatabaseSettings()
log_settings = LoggingSettings()