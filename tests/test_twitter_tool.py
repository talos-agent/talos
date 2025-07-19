import unittest
from unittest.mock import MagicMock, patch
from talos.tools.twitter import TwitterTool
from datetime import datetime, timezone

class TestTwitterTool(unittest.TestCase):
    @patch('os.environ')
    @patch('tweepy.API')
    @patch('tweepy.OAuthHandler')
    def test_evaluate_account(self, MockAuth, MockAPI, MockEnv):
        # Mock the Tweepy API
        mock_api = MockAPI.return_value
        mock_user = MagicMock()
        mock_user.followers_count = 1000
        mock_user.friends_count = 100
        mock_user.created_at = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        mock_user.verified = True
        mock_user.default_profile_image = False
        mock_api.get_user.return_value = mock_user

        # Create an instance of the TwitterTool
        twitter_tool = TwitterTool()
        twitter_tool.api = mock_api

        # Call the evaluate_account method
        result = twitter_tool.evaluate_account('test_user')

        # Assert the results
        self.assertEqual(result['score'], 5)
        self.assertEqual(result['follower_following_ratio'], 10)
        self.assertGreater(result['account_age_days'], 365)
        self.assertTrue(result['is_verified'])
        self.assertFalse(result['is_default_profile_image'])

if __name__ == '__main__':
    unittest.main()
