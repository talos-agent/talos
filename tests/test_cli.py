from treasury_agent.cli import main
import pytest

def test_main(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    captured = capsys.readouterr()
    assert "Treasury Agent CLI" in captured.out
