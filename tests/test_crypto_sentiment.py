import os
from unittest import mock

from talos.disciplines.crypto_sentiment import post_question, analyze_sentiment, TWEET_ID_FILE


@mock.patch.dict(os.environ, {
    "TWITTER_CONSUMER_KEY": "test",
    "TWITTER_CONSUMER_SECRET": "test",
    "TWITTER_ACCESS_TOKEN": "test",
    "TWITTER_ACCESS_TOKEN_SECRET": "test",
})
@mock.patch("talos.disciplines.crypto_sentiment.get_api")
def test_post_question(mock_get_api):
    mock_api = mock.MagicMock()
    mock_get_api.return_value = mock_api
    mock_tweet = mock.MagicMock()
    mock_tweet.id = "12345"
    mock_api.update_status.return_value = mock_tweet

    # Create a mock for the open function
    m = mock.mock_open()
    with mock.patch("builtins.open", m, create=True):
        post_question()

    # Check that the tweet was posted
    mock_api.update_status.assert_called_once_with(
        status="What is your current sentiment about crypto markets today and why?"
    )

    # Check that the tweet ID was saved to the file
    m.assert_called_once_with(TWEET_ID_FILE, "w")
    m().write.assert_called_once_with("12345")


@mock.patch.dict(os.environ, {
    "TWITTER_CONSUMER_KEY": "test",
    "TWITTER_CONSUMER_SECRET": "test",
    "TWITTER_ACCESS_TOKEN": "test",
    "TWITTER_ACCESS_TOKEN_SECRET": "test",
    "OPENAI_API_KEY": "test",
})
@mock.patch("talos.disciplines.crypto_sentiment.get_api")
@mock.patch("talos.disciplines.crypto_sentiment.CoreAgent")
def test_analyze_sentiment(mock_core_agent, mock_get_api):
    mock_api = mock.MagicMock()
    mock_get_api.return_value = mock_api

    # Mock the API calls
    mock_user = mock.MagicMock()
    mock_user.screen_name = "testuser"
    mock_api.verify_credentials.return_value = mock_user

    mock_reply = mock.MagicMock()
    mock_reply.text = "I am bullish on crypto!"
    mock_reply.in_reply_to_status_id_str = "12345"
    mock_reply.user.screen_name = "test_user"
    mock_reply.user.followers_count = 100

    mock_cursor = mock.MagicMock()
    mock_cursor.items.return_value = [mock_reply]
    mock_api.search_tweets.return_value = [mock_reply]

    # Mock the CoreAgent
    mock_agent_instance = mock_core_agent.return_value
    mock_agent_instance.run.return_value.answers = [{"answer": "80"}]


    # Create a mock for the open function
    m = mock.mock_open(read_data="12345")
    with mock.patch("builtins.open", m, create=True):
        analyze_sentiment()

    # Assert that the summary tweet was posted
    mock_api.update_status.assert_called_once()
    call_args = mock_api.update_status.call_args
    summary = call_args[1]["status"]
    assert "Crypto Sentiment Score: 80/100" in summary
    assert "Most interesting reply from @test_user (100 followers):" in summary
    assert "I am bullish on crypto!" in summary
