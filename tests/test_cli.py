from unittest.mock import patch

import pytest

from conversational.cli import main


from research.models import QueryResponse, QueryResult


@patch("conversational.cli.MainAgent")
def test_main(mock_main_agent, capsys: pytest.CaptureFixture[str]) -> None:
    # Arrange
    mock_agent_instance = mock_main_agent.return_value
    mock_agent_instance.run.return_value = QueryResponse(
        answers=[
            QueryResult(
                answer="Hello, world!",
                context=None,
                document_id=None,
                meta=None,
                score=1.0,
            )
        ]
    )

    # Act
    with patch("builtins.input", side_effect=["Hello", "exit"]):
        main()

    # Assert
    captured = capsys.readouterr()
    assert "Treasury Agent CLI" in captured.out
    assert "Hello, world!" in captured.out
