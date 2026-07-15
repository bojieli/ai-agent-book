"""Configuration management for Collaboration Tools MCP Server."""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BrowserConfig(BaseModel):
    """Browser automation configuration."""
    headless: bool = Field(default=False)
    user_data_dir: str = Field(default="~/.config/collaboration-tools/browser")
    timeout: int = Field(default=30000)


class EmailConfig(BaseModel):
    """Email notification configuration."""
    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    smtp_use_tls: bool = Field(default=True)
    sendgrid_api_key: Optional[str] = None


class IMConfig(BaseModel):
    """Instant messaging configuration."""
    telegram_bot_token: Optional[str] = None
    telegram_default_chat_id: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None


class HITLConfig(BaseModel):
    """Human-in-the-loop configuration."""
    admin_email: Optional[str] = None
    webhook_url: Optional[str] = None
    timeout_seconds: int = Field(default=3600)


class TimerConfig(BaseModel):
    """Timer management configuration."""
    storage_path: str = Field(default="~/.config/collaboration-tools/timers.json")


class Config(BaseModel):
    """Main configuration object."""
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    im: IMConfig = Field(default_factory=IMConfig)
    hitl: HITLConfig = Field(default_factory=HITLConfig)
    timer: TimerConfig = Field(default_factory=TimerConfig)
    log_level: str = Field(default="INFO")


def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        browser=BrowserConfig(
            headless=os.getenv("BROWSER_HEADLESS", "false").lower() == "true",
            user_data_dir=os.getenv("BROWSER_USER_DATA_DIR", "~/.config/collaboration-tools/browser"),
            timeout=int(os.getenv("BROWSER_TIMEOUT", "30000"))
        ),
        email=EmailConfig(
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_username=os.getenv("SMTP_USERNAME"),
            smtp_password=os.getenv("SMTP_PASSWORD"),
            smtp_from_email=os.getenv("SMTP_FROM_EMAIL"),
            smtp_use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
            sendgrid_api_key=os.getenv("SENDGRID_API_KEY")
        ),
        im=IMConfig(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            telegram_default_chat_id=os.getenv("TELEGRAM_DEFAULT_CHAT_ID"),
            slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
            discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL")
        ),
        hitl=HITLConfig(
            admin_email=os.getenv("HITL_ADMIN_EMAIL"),
            webhook_url=os.getenv("HITL_WEBHOOK_URL"),
            timeout_seconds=int(os.getenv("HITL_TIMEOUT_SECONDS", "3600"))
        ),
        timer=TimerConfig(
            storage_path=os.getenv("TIMER_STORAGE_PATH", "~/.config/collaboration-tools/timers.json")
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )


# Global config instance
config = load_config()
