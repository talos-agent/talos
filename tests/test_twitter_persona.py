import unittest
from unittest.mock import MagicMock

from talos.services.implementations.twitter_persona import TwitterPersonaService
from talos.tools.twitter import TwitterTool, TwitterToolName


class TestTwitterPersona(unittest.TestCase):
    def test_generate_persona_prompt(self):
        # Create a mock Twitter client
        mock_twitter_client = MagicMock()

        # Mock the API responses
        mock_tweet = MagicMock()
        mock_tweet.text = "This is a test tweet."
        mock_tweet.in_reply_to_screen_name = "testuser"
        mock_tweet.in_reply_to_status_id = "12345"

        mock_original_tweet = MagicMock()
        mock_original_tweet.text = "This is the original tweet."
        mock_original_tweet.user.screen_name = "original_user"

        mock_twitter_client.get_user_timeline.return_value = [mock_tweet]
        mock_twitter_client.get_user_mentions.return_value = [mock_tweet]
        mock_twitter_client.get_tweet.return_value = mock_original_tweet

        # Create the TwitterPersonaService with the mock client
        persona_service = TwitterPersonaService(twitter_client=mock_twitter_client)

        # Run the service
        response = persona_service.run(username="testuser")

        # Check the output
        self.assertIn("Emulate the voice and style", response.answers[0])
        self.assertIn("This is a test tweet.", response.answers[0])
        self.assertIn("In reply to @original_user", response.answers[0])
        self.assertIn("This is the original tweet.", response.answers[0])

    def test_twitter_tool_generate_persona_prompt(self):
        # Create a mock Twitter client
        mock_twitter_client = MagicMock()

        # Mock the API responses
        mock_tweet = MagicMock()
        mock_tweet.text = "This is a test tweet."
        mock_tweet.in_reply_to_screen_name = "testuser"
        mock_tweet.in_reply_to_status_id = "12345"

        mock_original_tweet = MagicMock()
        mock_original_tweet.text = "This is the original tweet."
        mock_original_tweet.user.screen_name = "original_user"

        mock_twitter_client.get_user_timeline.return_value = [mock_tweet]
        mock_twitter_client.get_user_mentions.return_value = [mock_tweet]
        mock_twitter_client.get_tweet.return_value = mock_original_tweet

        # Create the TwitterTool with the mock client
        twitter_tool = TwitterTool(twitter_client=mock_twitter_client)

        # Run the tool
        response = twitter_tool._run(tool_name=TwitterToolName.GENERATE_PERSONA_PROMPT, username="testuser")

        # Check the output
        self.assertIn("Emulate the voice and style", response)
        self.assertIn("This is a test tweet.", response)
        self.assertIn("In reply to @original_user", response)
        self.assertIn("This is the original tweet.", response)


if __name__ == "__main__":
    unittest.main()
