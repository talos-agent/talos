import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager
from talos.skills.twitter_persona import TwitterPersonaSkill
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

    def get_sentiment(self, search_query: str = "talos") -> float:
        return 0.5

    def post_tweet(self, tweet: str) -> Any:
        pass

    def reply_to_tweet(self, tweet_id: str, tweet: str) -> Any:
        pass


class MockPromptManager(PromptManager):
    def get_prompt(self, name: str) -> Prompt | None:
        return Prompt(name="test_prompt", template="This is a test prompt.", input_variables=[])


class TestTwitterPersona(unittest.TestCase):
    @patch("talos.skills.twitter_persona.ChatOpenAI")
    def test_generate_persona_prompt(self, MockChatOpenAI):
        # Create mocks
        mock_twitter_client = MockTwitterClient()
        mock_prompt_manager = MockPromptManager()
        mock_llm = MockChatOpenAI.return_value
        
        from talos.models.twitter import TwitterPersonaResponse
        mock_structured_llm = MagicMock()
        mock_structured_llm.invoke.return_value = TwitterPersonaResponse(
            report="This is a persona description.",
            topics=["technology", "startups"],
            style=["analytical", "technical"]
        )
        mock_llm.with_structured_output.return_value = mock_structured_llm

        # Mock the API responses
        mock_tweet = MagicMock()
        mock_tweet.text = "This is a test tweet."
        mock_tweet.get_replied_to_id.return_value = None

        mock_twitter_client.get_user_timeline = MagicMock(return_value=[mock_tweet])
        mock_twitter_client.get_user_mentions = MagicMock(return_value=[mock_tweet])

        # Create the TwitterPersonaSkill with the mock client
        persona_skill = TwitterPersonaSkill(
            twitter_client=mock_twitter_client,
            prompt_manager=mock_prompt_manager,
            llm=mock_llm,
        )

        # Run the skill
        response = persona_skill.run(username="testuser")

        # Check the output
        self.assertIsInstance(response, TwitterPersonaResponse)
        self.assertEqual(response.report, "This is a persona description.")
        self.assertEqual(response.topics, ["technology", "startups"])
        self.assertEqual(response.style, ["analytical", "technical"])
        mock_llm.with_structured_output.assert_called_once_with(TwitterPersonaResponse)

    def test_twitter_tool_generate_persona_prompt(self):
        # Create a mock Twitter client
        mock_twitter_client = MockTwitterClient()

        # Create the TwitterTool with the mock client
        twitter_tool = TwitterTool(twitter_client=mock_twitter_client)

        # Run the tool
        with patch(
            "talos.tools.twitter.TwitterPersonaSkill",
        ) as MockTwitterPersonaSkill:
            from talos.models.twitter import TwitterPersonaResponse
            mock_persona_skill = MockTwitterPersonaSkill.return_value
            mock_persona_skill.run.return_value = TwitterPersonaResponse(
                report="This is a rendered prompt.",
                topics=["crypto", "trading"],
                style=["confident", "data-driven"]
            )
            response = twitter_tool._run(tool_name=TwitterToolName.GENERATE_PERSONA_PROMPT, username="testuser")

        # Check the output - should return just the report
        self.assertEqual(response, "This is a rendered prompt.")


if __name__ == "__main__":
    unittest.main()
