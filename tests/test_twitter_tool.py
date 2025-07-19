import unittest
from unittest.mock import MagicMock
from talos.tools.twitter import TwitterTool
from talos.tools.twitter_client import TwitterClient
from talos.tools.twitter_evaluator import TwitterAccountEvaluator
from talos.models.evaluation import EvaluationResult
from datetime import datetime, timezone

class MockTwitterClient(TwitterClient):
    def get_user(self, username: str):
        return MagicMock()

class MockTwitterAccountEvaluator(TwitterAccountEvaluator):
    def evaluate(self, user: any) -> EvaluationResult:
        return EvaluationResult(
            score=75,
            additional_data={
                "follower_following_ratio": 10,
                "account_age_days": 1000,
                "is_verified": True,
                "is_default_profile_image": False,
            }
        )

class TestTwitterTool(unittest.TestCase):
    def test_evaluate_account(self):
        # Create mock dependencies
        mock_twitter_client = MockTwitterClient()
        mock_account_evaluator = MockTwitterAccountEvaluator()

        # Create an instance of the TwitterTool with the mock client and evaluator
        twitter_tool = TwitterTool(twitter_client=mock_twitter_client, account_evaluator=mock_account_evaluator)

        # Call the evaluate_account method
        result = twitter_tool.evaluate_account('test_user')

        # Assert the results
        self.assertEqual(result.score, 75)
        self.assertEqual(result.additional_data['follower_following_ratio'], 10)
        self.assertGreater(result.additional_data['account_age_days'], 365)
        self.assertTrue(result.additional_data['is_verified'])
        self.assertFalse(result.additional_data['is_default_profile_image'])

if __name__ == '__main__':
    unittest.main()
