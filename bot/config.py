"""Configuration for the LMS Telegram bot.

Loads settings from .env.bot.secret using environment variables.
In test mode, BOT_TOKEN is not required.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def _load_env_files() -> None:
    """Load .env.bot.secret from the repo root and bot directory if present."""
    bot_dir = Path(__file__).parent
    repo_root = bot_dir.parent

    for env_path in (repo_root / ".env.bot.secret", bot_dir / ".env.bot.secret"):
        if env_path.exists():
            load_dotenv(env_path, override=True)


_load_env_files()


class Config:
    """Bot configuration from environment variables."""

    BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")
    """Telegram bot token from BotFather. Required for Telegram mode."""

    LMS_API_BASE_URL: str = os.getenv("LMS_API_BASE_URL", "http://localhost:42002")
    """Base URL of the LMS backend API."""

    LMS_API_KEY: str = os.getenv("LMS_API_KEY", "")
    """Bearer token for LMS API authentication."""

    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    """API key for LLM service (Qwen Code or OpenRouter)."""

    LLM_API_BASE_URL: str = os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1")
    """Base URL for LLM API."""

    LLM_API_MODEL: str = os.getenv("LLM_API_MODEL", "coder")
    """LLM model name to use."""

    @classmethod
    def validate_for_telegram(cls) -> None:
        """Validate that required settings for Telegram mode are present."""
        if not cls.BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN not set in .env.bot.secret. "
                "Get it from BotFather: https://t.me/BotFather"
            )

    @classmethod
    def validate_for_lms(cls) -> None:
        """Validate that LMS API settings are present."""
        if not cls.LMS_API_KEY:
            raise ValueError("LMS_API_KEY not set in .env.bot.secret")


config = Config()
