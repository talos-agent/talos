import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from talos.services.implementations.talos_sentiment import TalosSentimentService
from talos.skills.talos_sentiment_skill import TalosSentimentSkill


def test_talos_sentiment_service_run():
    with (
        patch("talos.services.implementations.talos_sentiment.TweepyClient") as mock_tweepy_client_class,
        patch("talos.services.implementations.talos_sentiment.LLMClient") as mock_llm_client_class,
    ):
        # Mock the TweepyClient
        mock_tweet = MagicMock()
        mock_tweet.text = "This is a test tweet about Talos."
        mock_tweet.author.screen_name = "test_user"
        mock_tweet.author.followers_count = 100
        mock_tweet.retweet_count = 10
        mock_tweet.favorite_count = 20
        mock_tweet.created_at = datetime.now(timezone.utc)
        mock_twitter_client = mock_tweepy_client_class.return_value
        mock_twitter_client.search_tweets.return_value = [mock_tweet]

        # Mock the LLMClient
        mock_llm_client = mock_llm_client_class.return_value
        mock_llm_client.reasoning.side_effect = [
            json.dumps({"sentiments": [{"score": 75, "explanation": "This is a test explanation."}]}),
            "This is a test summary.",
        ]

        service = TalosSentimentService()
        response = service.run(search_query="talos")

        # Assert that the llm was called with the correct arguments
        tweet_data = [
            {
                "text": "This is a test tweet about Talos.",
                "author": "test_user",
                "followers": 100,
                "engagement": 30,
                "age_in_days": 0,
            }
        ]
        expected_sentiment_prompt = service.sentiment_prompt.format(tweets=json.dumps(tweet_data))
        expected_summary_prompt = service.summary_prompt.format(
            results=json.dumps([{"score": 75, "explanation": "This is a test explanation."}])
        )
        mock_llm_client.reasoning.assert_any_call(expected_sentiment_prompt)
        mock_llm_client.reasoning.assert_any_call(expected_summary_prompt)

        # Assert that the response is correct
        assert response.score == 75.00
        assert "The weighted average sentiment score is 75.00 out of 100." in response.answers[0]
        assert "This is a test summary." in response.answers[0]
        assert "This is a test explanation." in response.answers[0]


def test_talos_sentiment_skill_get_sentiment():
    with (
        patch("talos.services.implementations.talos_sentiment.TweepyClient"),
        patch("talos.services.implementations.talos_sentiment.LLMClient"),
    ):
        with patch("talos.skills.talos_sentiment_skill.TalosSentimentService") as mock_service_class:
            mock_service_instance = mock_service_class.return_value
            mock_service_instance.run.return_value.score = 75.00
            mock_service_instance.run.return_value.answers = [
                "Searched for 'talos' and analyzed 1 tweets.\\n"
                "The weighted average sentiment score is 75.00 out of 100.\\n\\n"
                "**Summary:** This is a test summary.\\n\\n"
                "Here are some of the tweets that were analyzed:\\n"
                "- **@test_user** (100 followers, 30 engagement, 0 days old): This is a test explanation.\\n"
            ]

            skill = TalosSentimentSkill()
            result = skill.get_sentiment(search_query="talos")

            # Assert that the result is correct
            assert result["score"] == 75.00
            assert "The weighted average sentiment score is 75.00 out of 100." in result["report"]
