from unittest.mock import Mock
from thread_sentiment import main

def test_import():
    assert main is not None

def test_analyze_sentiment():
    # Mock the Agent class
    main.Agent = Mock()

    # Mock the run method
    main.Agent.return_value.run.return_value.content = "The sentiment is positive."

    # Call the function
    sentiment = main.analyze_sentiment(["This is a great tweet!"])

    # Assert the result
    assert sentiment == "The sentiment is positive."
