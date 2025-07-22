import json
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
        mock_twitter_client = mock_tweepy_client_class.return_value
        mock_twitter_client.search_tweets.return_value = [mock_tweet]

        # Mock the LLMClient
        mock_llm_client = mock_llm_client_class.return_value
        mock_llm_client.reasoning.return_value = json.dumps({"score": 75, "explanation": "This is a test explanation."})

        service = TalosSentimentService()
        response = service.run(search_query="talos")

        # Assert that the llm was called with the correct arguments
        mock_llm_client.reasoning.assert_called_once_with(
            "Analyze the sentiment of the following tweet, returning a score from 0 to 100 (0 being very negative, 100 being very positive) and a brief explanation of your reasoning. Return your response as a JSON object with the keys 'score' and 'explanation'.",
            "This is a test tweet about Talos.",
        )

        # Assert that the response is correct
        assert "The average sentiment score is 75.00 out of 100." in response.answers[0]
        assert "This is a test explanation." in response.answers[0]


def test_talos_sentiment_skill_get_sentiment():
    with (
        patch("talos.services.implementations.talos_sentiment.TweepyClient"),
        patch("talos.services.implementations.talos_sentiment.LLMClient"),
    ):
        with patch("talos.skills.talos_sentiment_skill.TalosSentimentService") as mock_service_class:
            mock_service_instance = mock_service_class.return_value
            mock_service_instance.run.return_value.answers = [
                "Searched for 'talos' and analyzed 1 tweets.\\n"
                "The average sentiment score is 75.00 out of 100.\\n\\n"
                "Here are some of the explanations:\\n"
                "- This is a test explanation.\\n"
            ]

            skill = TalosSentimentSkill()
            result = skill.get_sentiment(search_query="talos")

            # Assert that the result is correct
            assert result["score"] == 75.00
            assert "The average sentiment score is 75.00 out of 100." in result["report"]
