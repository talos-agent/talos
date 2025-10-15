from __future__ import annotations

import unittest
from unittest.mock import patch

from talos.nexus.service import NexusService


class TestNexusService(unittest.TestCase):
    @patch("talos.nexus.service.nexus_graph")
    def test_run_nexus_service(self, mock_nexus_graph):
        # Arrange
        mock_nexus_graph.invoke.return_value = {"messages": ["Message from Node A", "Message from Node B"]}
        service = NexusService()
        messages = ["Initial message"]

        # Act
        result = service.run(messages)

        # Assert
        self.assertIn("messages", result)
        self.assertEqual(len(result["messages"]), 2)
        mock_nexus_graph.invoke.assert_called_once_with({"messages": messages})


if __name__ == "__main__":
    unittest.main()
