from unittest.mock import Mock, patch
from thread_sentiment import main

def test_import():
    assert main is not None

@patch("thread_sentiment.main.prompt_manager")
def test_analyze_sentiment(mock_prompt_manager):
    # Mock the Agent class
    main.Agent = Mock()

    # Mock the run method
    main.Agent.return_value.run.return_value.content = "The sentiment is positive."

    # Mock the prompt manager
    mock_prompt_manager.get_prompt.return_value.template = "test"

    # Call the function
    sentiment = main.analyze_sentiment([{"text": "This is a great tweet!", "followers": 100}])

    # Assert the result
    assert sentiment == "The sentiment is positive."
