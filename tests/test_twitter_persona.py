import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager
from talos.services.implementations.twitter_persona import TwitterPersonaService
from talos.tools.twitter import TwitterTool, TwitterToolName
from talos.tools.twitter_client import TwitterClient


class MockTwitterClient(TwitterClient):
    def get_user(self, username: str) -> Any:
        pass

    def search_tweets(self, query: str) -> list[Any]:
        return []

    def get_user_timeline(self, username: str) -> list[Any]:
        return []

    def get_user_mentions(self, username: str) -> list[Any]:
        return []

    def get_tweet(self, tweet_id: str) -> Any:
        pass


class MockPromptManager(PromptManager):
    def get_prompt(self, name: str) -> Prompt | None:
        return Prompt(name="test_prompt", template="This is a test prompt.", input_variables=[])


class TestTwitterPersona(unittest.TestCase):
    @patch("talos.services.implementations.twitter_persona.ChatOpenAI")
    def test_generate_persona_prompt(self, MockChatOpenAI):
        # Create mocks
        mock_twitter_client = MockTwitterClient()
        mock_prompt_manager = MockPromptManager()
        mock_llm = MockChatOpenAI.return_value
        mock_llm.invoke.return_value.content = "This is a persona description."

        # Mock the API responses
        mock_tweet = MagicMock()
        mock_tweet.text = "This is a test tweet."
        mock_tweet.in_reply_to_screen_name = "testuser"
        mock_tweet.in_reply_to_status_id = "12345"

        mock_original_tweet = MagicMock()
        mock_original_tweet.text = "This is the original tweet."
        mock_original_tweet.user.screen_name = "original_user"

        mock_twitter_client.get_user_timeline = MagicMock(return_value=[mock_tweet])
        mock_twitter_client.get_user_mentions = MagicMock(return_value=[mock_tweet])
        mock_twitter_client.get_tweet = MagicMock(return_value=mock_original_tweet)

        # Create the TwitterPersonaService with the mock client
        persona_service = TwitterPersonaService(
            twitter_client=mock_twitter_client,
            prompt_manager=mock_prompt_manager,
            llm=mock_llm,
        )

        # Run the service
        response = persona_service.run(username="testuser")

        # Check the output
        self.assertEqual(response.answers[0], "This is a persona description.")
        mock_llm.invoke.assert_called_once()

    def test_twitter_tool_generate_persona_prompt(self):
        # Create a mock Twitter client
        mock_twitter_client = MockTwitterClient()

        # Mock the API responses
        mock_tweet = MagicMock()
        mock_tweet.text = "This is a test tweet."
        mock_tweet.in_reply_to_screen_name = "testuser"
        mock_tweet.in_reply_to_status_id = "12345"

        mock_original_tweet = MagicMock()
        mock_original_tweet.text = "This is the original tweet."
        mock_original_tweet.user.screen_name = "original_user"

        mock_twitter_client.get_user_timeline = MagicMock(return_value=[mock_tweet])
        mock_twitter_client.get_user_mentions = MagicMock(return_value=[mock_tweet])
        mock_twitter_client.get_tweet = MagicMock(return_value=mock_original_tweet)

        # Create the TwitterTool with the mock client
        twitter_tool = TwitterTool(twitter_client=mock_twitter_client)

        # Run the tool
        with patch(
            "talos.tools.twitter.TwitterPersonaService",
        ) as MockTwitterPersonaService:
            mock_persona_service = MockTwitterPersonaService.return_value
            mock_persona_service.run.return_value.answers = ["This is a rendered prompt."]
            response = twitter_tool._run(tool_name=TwitterToolName.GENERATE_PERSONA_PROMPT, username="testuser")

        # Check the output
        self.assertEqual(response, "This is a rendered prompt.")


if __name__ == "__main__":
    unittest.main()
