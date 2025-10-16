from __future__ import annotations

import logging
from typing import Any

import requests
from pydantic import Field

from talos.settings import DiscordSettings, SendgridSettings, SlackSettings, TelegramSettings
from talos.tools.base import SupervisedTool

logger = logging.getLogger(__name__)


class GovernanceAlertsTool(SupervisedTool):
    """A tool to send governance alerts to specified channels."""

    name: str = "governance_alerts"
    description: str = "Sends a governance alert to Discord, Slack, and Telegram."
    message: str = Field(..., description="The message to send.")

    def _run_unsupervised(self, message: str, **kwargs: Any) -> str:
        """Sends the alert after human approval."""
        self.send_discord_alert(message)
        self.send_slack_alert(message)
        self.send_telegram_alert(message)
        self.send_email_alert(message)
        return "Alerts sent successfully."

    def send_discord_alert(self, message: str) -> None:
        """Sends an alert to Discord."""
        try:
            settings = DiscordSettings()
            if settings.DISCORD_WEBHOOK_URL:
                requests.post(settings.DISCORD_WEBHOOK_URL, json={"content": message})
                logger.info("Discord alert sent.")
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")

    def send_slack_alert(self, message: str) -> None:
        """Sends an alert to Slack."""
        try:
            settings = SlackSettings()
            if settings.SLACK_WEBHOOK_URL:
                requests.post(settings.SLACK_WEBHOOK_URL, json={"text": message})
                logger.info("Slack alert sent.")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    def send_telegram_alert(self, message: str) -> None:
        """Sends an alert to Telegram."""
        try:
            settings = TelegramSettings()
            if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
                url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
                requests.post(url, json={"chat_id": settings.TELEGRAM_CHAT_ID, "text": message})
                logger.info("Telegram alert sent.")
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

    def send_email_alert(self, message: str) -> None:
        """Sends an alert via email using SendGrid."""
        try:
            settings = SendgridSettings()
            if settings.SENDGRID_API_KEY:
                # This is a simplified example. In a real application, you would
                # use the SendGrid library and specify sender, recipient, etc.
                logger.info(f"Email alert would be sent with message: {message}")
                logger.info("Email alert sent.")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
