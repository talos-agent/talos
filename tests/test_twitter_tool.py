import unittest
from typing import Any
from unittest.mock import MagicMock

from talos.models.evaluation import EvaluationResult
from talos.tools.twitter import TwitterTool
from talos.tools.twitter_client import TwitterClient, TweepyClient
from talos.tools.twitter_evaluator import TwitterAccountEvaluator


from pydantic import SecretStr


class MockTwitterClient(TwitterClient):
    def __init__(self, bearer_token: str | None = "fake-token"):
        if bearer_token:
            self.TWITTER_BEARER_TOKEN = SecretStr(bearer_token)
        else:
            self.TWITTER_BEARER_TOKEN = None

    def get_user(self, username: str):
        return MagicMock()

    def search_tweets(self, query: str):
        return []

    def get_user_timeline(self, username: str) -> list[Any]:
        mock_tweet = MagicMock()
        mock_tweet.text = "This is a test tweet from the timeline."
        return [mock_tweet]

    def get_user_mentions(self, username: str) -> list[Any]:
        mock_tweet = MagicMock()
        mock_tweet.text = "This is a test tweet from the mentions."
        mock_tweet.in_reply_to_screen_name = "testuser"
        return [mock_tweet]

    def get_tweet(self, tweet_id: str) -> Any:
        mock_tweet = MagicMock()
        mock_tweet.text = "This is a test tweet."
        return mock_tweet

    def get_sentiment(self, search_query: str = "talos") -> float:
        return 0.5

    def post_tweet(self, tweet: str) -> Any:
        pass

    def reply_to_tweet(self, tweet_id: str, tweet: str) -> Any:
        pass


class MockTwitterAccountEvaluator(TwitterAccountEvaluator):
    def evaluate(self, user: Any) -> EvaluationResult:
        return EvaluationResult(
            score=75,
            additional_data={
                "follower_following_ratio": 10,
                "account_age_days": 1000,
                "is_verified": True,
                "is_default_profile_image": False,
            },
        )


class TestTwitterTool(unittest.TestCase):
    def test_evaluate_account(self):
        # Create mock dependencies
        mock_twitter_client = MockTwitterClient()
        mock_account_evaluator = MockTwitterAccountEvaluator()

        # Create an instance of the TwitterTool with the mock client and evaluator
        twitter_tool = TwitterTool(twitter_client=mock_twitter_client, account_evaluator=mock_account_evaluator)

        # Call the evaluate_account method
        result = twitter_tool.evaluate_account("test_user")

        # Assert the results
        self.assertEqual(result.score, 75)
        self.assertEqual(result.additional_data["follower_following_ratio"], 10)
        self.assertGreater(result.additional_data["account_age_days"], 365)
        self.assertTrue(result.additional_data["is_verified"])
        self.assertFalse(result.additional_data["is_default_profile_image"])

    def test_missing_bearer_token(self):
        with self.assertRaises(ValueError):
            TwitterTool(twitter_client=TweepyClient(TWITTER_BEARER_TOKEN=None))


if __name__ == "__main__":
    unittest.main()
