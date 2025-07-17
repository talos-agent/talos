import unittest
from unittest.mock import MagicMock, patch

from conversational.letta_agent import LettaAgent
from research.models import RunParams


class TestLettaAgent(unittest.TestCase):
    @patch("conversational.letta_agent.letta.Letta")
    def test_run(self, mock_letta):
        # Arrange
        mock_sdk_instance = MagicMock()
        mock_letta.return_value = mock_sdk_instance

        mock_response = MagicMock()
        mock_response.content = "Hello, world!"
        mock_sdk_instance.agents.messages.create.return_value = mock_response

        agent = LettaAgent(api_key="test_key", agent_id="test_agent")

        # Act
        response = agent.run("Hello", params=RunParams())

        # Assert
        mock_sdk_instance.agents.messages.create.assert_called_once_with(
            agent_id="test_agent",
            content="Hello",
            stream=False,
        )
        self.assertEqual(response.answers[0].answer, "Hello, world!")

    def test_add_dataset(self):
        # Arrange
        agent = LettaAgent(api_key="test_key", agent_id="test_agent")

        # Act & Assert
        with self.assertRaises(NotImplementedError):
            agent.add_dataset("path/to/dataset", params=MagicMock())


if __name__ == "__main__":
    unittest.main()
