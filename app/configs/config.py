import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Central configuration for all environments"""

    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"

    # GitHub
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    GITHUB_WEBHOOK_SECRET: Optional[str] = os.getenv("GITHUB_WEBHOOK_SECRET", "default_secret")

    # Slack
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")

    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "metalflow")

    # ML Models
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/")
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "32"))

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls()

config = Config.from_env()
