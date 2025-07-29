import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, create_autospec

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable

from talos.core.agent import Agent
from talos.core.memory import Memory
from talos.tools.memory_tool import AddMemoryTool


class TestAddMemoryTool(unittest.TestCase):
    def test_run(self):
        from talos.core.agent import Agent

        # Create a mock agent
        agent = MagicMock(spec=Agent)
        # Create the tool
        AddMemoryTool.model_rebuild()
        tool = AddMemoryTool(agent=agent)
        # Run the tool
        description = "This is a test memory."
        result = tool._run(description)
        # Check that the agent's add_memory method was called
        agent.add_memory.assert_called_once_with(description)
        self.assertEqual(result, f"Stored in memory: {description}")


class TestAddMemoryToolIntegration(unittest.TestCase):
    def setUp(self):
        # Create a mock embeddings model
        class MockEmbeddings(Embeddings):
            def embed_documents(self, texts):
                return [[1.0] * 768 for _ in texts]

            def embed_query(self, text):
                return [1.0] * 768

        # Create a mock model
        mock_model = create_autospec(BaseChatModel)
        mock_model.with_structured_output.return_value = create_autospec(Runnable)

        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()

        # Create a mock agent
        self.agent = Agent(
            model=mock_model,
            memory=Memory(
                file_path=Path(self.temp_dir) / "test_memory.json",
                embeddings_model=MockEmbeddings(),
            ),
        )
        AddMemoryTool.model_rebuild()

    def tearDown(self) -> None:
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_run_integration(self):
        # Get the tool from the agent's tool manager
        tool = self.agent.tool_manager.get_tool("add_memory")
        self.assertIsInstance(tool, AddMemoryTool)

        # Run the tool
        description = "This is a test memory."
        result = tool._run(description)
        self.assertEqual(result, f"Stored in memory: {description}")

        # Check that the memory was added
        memories = self.agent.memory.search(description)
        self.assertIn(description, [m.description for m in memories])


if __name__ == "__main__":
    unittest.main()
