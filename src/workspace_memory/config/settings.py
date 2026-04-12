"""Central settings for storage, capture scope, and provider configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


LLMProviderName = Literal["anthropic", "openai"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="WORKSPACE_MEMORY_",
        extra="ignore",
    )

    data_dir: Path = Field(default=Path("./data"))
    log_level: str = Field(default="INFO")
    llm_provider: LLMProviderName = Field(default="anthropic")
    capture_roots: list[Path] = Field(default_factory=lambda: [Path.cwd()])
    excluded_dirs: list[str] = Field(
        default_factory=lambda: [
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "Dropbox/Private",
            "OneDrive/Personal",
        ]
    )
    excluded_extensions: list[str] = Field(
        default_factory=lambda: [
            ".env",
            ".pem",
            ".key",
            ".p12",
            ".pfx",
            ".cer",
            ".crt",
            ".jks",
            ".sqlite",
            ".db",
        ]
    )
    preview_max_chars: int = Field(default=500, ge=1, le=5000)


settings = Settings()
