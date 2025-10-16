import unittest
from unittest.mock import MagicMock, patch

from talos.tools.governance_alerts import GovernanceAlertsTool


class TestGovernanceAlertsTool(unittest.TestCase):
    @patch("talos.tools.governance_alerts.requests.post")
    @patch("talos.tools.governance_alerts.DiscordSettings")
    @patch("talos.tools.governance_alerts.SlackSettings")
    @patch("talos.tools.governance_alerts.TelegramSettings")
    @patch("talos.tools.governance_alerts.SendgridSettings")
    def test_send_alerts(
        self,
        mock_sendgrid_settings,
        mock_telegram_settings,
        mock_slack_settings,
        mock_discord_settings,
        mock_post,
    ):
        # Arrange
        mock_discord_settings.return_value.DISCORD_WEBHOOK_URL = "fake_discord_url"
        mock_slack_settings.return_value.SLACK_WEBHOOK_URL = "fake_slack_url"
        mock_telegram_settings.return_value.TELEGRAM_BOT_TOKEN = "fake_token"
        mock_telegram_settings.return_value.TELEGRAM_CHAT_ID = "fake_chat_id"
        mock_sendgrid_settings.return_value.SENDGRID_API_KEY = "fake_sendgrid_key"

        tool = GovernanceAlertsTool(message="Test alert")
        mock_post.return_value = MagicMock(status_code=200)

        # Act
        result = tool._run_unsupervised(message="Test alert")

        # Assert
        self.assertEqual(result, "Alerts sent successfully.")
        self.assertEqual(mock_post.call_count, 3)  # Discord, Slack, Telegram

        # Verify Discord call
        mock_post.assert_any_call("fake_discord_url", json={"content": "Test alert"})

        # Verify Slack call
        mock_post.assert_any_call("fake_slack_url", json={"text": "Test alert"})

        # Verify Telegram call
        mock_post.assert_any_call(
            "https://api.telegram.org/botfake_token/sendMessage",
            json={"chat_id": "fake_chat_id", "text": "Test alert"},
        )


if __name__ == "__main__":
    unittest.main()
