import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from talos.services.implementations.talos_sentiment import TalosSentimentService
from talos.skills.talos_sentiment_skill import TalosSentimentSkill


def test_talos_sentiment_service_run():
    with (
        patch("talos.services.implementations.talos_sentiment.TweepyClient", autospec=True) as mock_tweepy_client_class,
        patch("talos.services.implementations.talos_sentiment.LLMClient", autospec=True) as mock_llm_client_class,
        patch(
            "talos.services.implementations.talos_sentiment.FilePromptManager",
            autospec=True,
        ) as mock_prompt_manager_class,
    ):
        # Mock the PromptManager
        mock_prompt = MagicMock()
        mock_prompt.template = "This is a test prompt."
        mock_prompt_manager = mock_prompt_manager_class.return_value
        mock_prompt_manager.get_prompt.return_value = mock_prompt

        # Mock the TweepyClient with v2 API format
        mock_tweet = MagicMock()
        mock_tweet.text = "This is a test tweet about Talos."
        mock_tweet.author_id = "user123"
        mock_tweet.public_metrics = {
            "like_count": 20,
            "retweet_count": 10,
            "reply_count": 5,
            "quote_count": 3
        }
        mock_tweet.created_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        mock_user = {
            "id": "user123",
            "username": "test_user",
            "public_metrics": {"followers_count": 100}
        }
        
        mock_response = MagicMock()
        mock_response.data = [mock_tweet]
        mock_response.includes = {"users": [mock_user]}
        
        mock_twitter_client = mock_tweepy_client_class.return_value
        mock_twitter_client.search_tweets.return_value = mock_response

        # Mock the LLMClient
        mock_llm_client = mock_llm_client_class.return_value
        mock_llm_client.reasoning.return_value = json.dumps({"score": 75, "report": "This is a test report."})

        service = TalosSentimentService(
            prompt_manager=mock_prompt_manager,
            twitter_client=mock_twitter_client,
            llm_client=mock_llm_client,
        )
        response = service.analyze_sentiment(search_query="talos")

        # Assert that the llm was called with the correct arguments
        expected_tweet_data = [
            {
                "text": "This is a test tweet about Talos.",
                "author": "test_user",
                "followers": 100,
                "likes": 20,
                "retweets": 10,
                "replies": 5,
                "quotes": 3,
                "total_engagement": 38,
                "engagement_rate": 38.0,
                "age_in_days": 0,
            }
        ]
        expected_sentiment_prompt = mock_prompt.template.format(tweets=json.dumps(expected_tweet_data))
        mock_llm_client.reasoning.assert_called_once_with(expected_sentiment_prompt)

        # Assert that the response is correct
        assert response.score == 75
        assert response.answers[0] == "This is a test report."


def test_talos_sentiment_skill_get_sentiment():
    with (
        patch("talos.services.implementations.talos_sentiment.TweepyClient", autospec=True),
        patch("talos.services.implementations.talos_sentiment.LLMClient", autospec=True),
    ):
        with patch("talos.skills.talos_sentiment_skill.TalosSentimentService", autospec=True) as mock_service_class:
            mock_service_instance = mock_service_class.return_value
            mock_service_instance.analyze_sentiment.return_value.score = 75
            mock_service_instance.analyze_sentiment.return_value.answers = ["This is a test report."]

            skill = TalosSentimentSkill(sentiment_service=mock_service_instance)
            result = skill.run(search_query="talos")

            # Assert that the result is correct
            assert result["score"] == 75
            assert result["report"] == "This is a test report."
