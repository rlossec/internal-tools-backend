
from dotenv import load_dotenv

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Config(BaseSettings):
    app_name: str = "Internal Tools API"
    debug: bool = False

    # Database configuration with defaults
    db_username: str = Field(default="dev", alias="POSTGRES_USER")
    db_password: str = Field(default="dev123", alias="POSTGRES_PASSWORD")
    db_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    db_port: int = Field(default=5433, alias="POSTGRES_PORT")
    db_name: str = Field(default="internal_tools", alias="POSTGRES_DATABASE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True
    )

    @property
    def db_url(self) -> str:
        return f"postgresql://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


config = Config()
