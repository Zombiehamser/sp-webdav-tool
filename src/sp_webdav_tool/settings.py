from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SP_WEBDAV_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    url: str = Field(..., description="WebDAV server base URL")
    path: str = Field("/webdav/MAIN.json", description="Path to MAIN.json on WebDAV")
    username: str = Field(..., description="WebDAV username")
    password: SecretStr = Field(..., description="WebDAV password")
    timeout: int = Field(10, ge=1, le=120)
    retry_count: int = Field(3, ge=1, le=10)
    backup_dir: Path = Field(
        default_factory=lambda: Path.home() / ".sp-webdav-tool" / "backups"
    )

    @property
    def webdav_file_url(self) -> str:
        return f"{self.url.rstrip('/')}/{self.path.lstrip('/')}"