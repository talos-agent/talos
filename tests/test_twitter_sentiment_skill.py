from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from talos.skills.twitter_sentiment import TwitterSentimentSkill
from talos.models.services import TwitterSentimentResponse


@patch("talos.skills.twitter_sentiment.FilePromptManager")
@patch("talos.skills.twitter_sentiment.TweepyClient")
@patch("talos.skills.twitter_sentiment.ChatOpenAI")
@patch("talos.tools.twitter_client.TwitterConfig")
def test_twitter_sentiment_skill_structured_output(mock_twitter_config, mock_llm_class, mock_tweepy_client_class, mock_prompt_manager_class):
    mock_prompt = MagicMock()
    mock_prompt.template = "Analyze sentiment: {results}"
    mock_prompt_manager = mock_prompt_manager_class.return_value
    mock_prompt_manager.get_prompt.return_value = mock_prompt

    mock_tweet = MagicMock()
    mock_tweet.text = "This is a positive tweet about the query."
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
        "public_metrics": {"followers_count": 1000}
    }
    
    mock_response = MagicMock()
    mock_response.data = [mock_tweet]
    mock_response.includes = {"users": [mock_user]}
    
    mock_twitter_client = mock_tweepy_client_class.return_value
    mock_twitter_client.search_tweets.return_value = mock_response

    mock_llm_response = MagicMock()
    mock_llm_response.content = "The sentiment is very positive with great engagement."
    mock_llm = mock_llm_class.return_value
    mock_llm.invoke.return_value = mock_llm_response

    skill = TwitterSentimentSkill()
    response = skill.run(query="test query")

    assert isinstance(response, TwitterSentimentResponse)
    assert response.score is not None
    assert 0 <= response.score <= 100
    assert len(response.answers) == 1
    assert "Sentiment Analysis Report" in response.answers[0]
    assert "Overall Score:" in response.answers[0]


@patch("talos.skills.twitter_sentiment.FilePromptManager")
@patch("talos.skills.twitter_sentiment.TweepyClient")
@patch("talos.skills.twitter_sentiment.ChatOpenAI")
@patch("talos.tools.twitter_client.TwitterConfig")
def test_twitter_sentiment_skill_no_tweets(mock_twitter_config, mock_llm_class, mock_tweepy_client_class, mock_prompt_manager_class):
    
    mock_response = MagicMock()
    mock_response.data = None
    
    mock_twitter_client = mock_tweepy_client_class.return_value
    mock_twitter_client.search_tweets.return_value = mock_response

    skill = TwitterSentimentSkill()
    response = skill.run(query="test query")

    assert isinstance(response, TwitterSentimentResponse)
    assert response.score is None
    assert "Could not find any tweets" in response.answers[0]
