from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_path: Path = Path("./users.db")
    jwt_secret_key: str = Field(
        default="replace-this-development-secret-with-at-least-32-characters",
        min_length=32,
    )
    jwt_algorithm: str = "HS256"