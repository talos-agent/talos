import unittest

from langchain_core.tools import BaseTool

from talos.tools.tool_manager import ToolManager


class MockTool(BaseTool):
    name: str = "mock_tool"
    description: str = "A mock tool for testing."

    def _run(self, *args, **kwargs):
        pass


class TestToolManager(unittest.TestCase):
    def setUp(self):
        self.tool_manager = ToolManager()

    def test_register_tool(self):
        tool = MockTool()
        self.tool_manager.register_tool(tool)
        self.assertIn("mock_tool", self.tool_manager.tools)

    def test_register_duplicate_tool(self):
        tool = MockTool()
        self.tool_manager.register_tool(tool)
        with self.assertRaises(ValueError):
            self.tool_manager.register_tool(tool)

    def test_unregister_tool(self):
        tool = MockTool()
        self.tool_manager.register_tool(tool)
        self.tool_manager.unregister_tool("mock_tool")
        self.assertNotIn("mock_tool", self.tool_manager.tools)

    def test_unregister_nonexistent_tool(self):
        with self.assertRaises(ValueError):
            self.tool_manager.unregister_tool("nonexistent_tool")

    def test_get_tool(self):
        tool = MockTool()
        self.tool_manager.register_tool(tool)
        retrieved_tool = self.tool_manager.get_tool("mock_tool")
        self.assertEqual(retrieved_tool, tool)

    def test_get_nonexistent_tool(self):
        with self.assertRaises(ValueError):
            self.tool_manager.get_tool("nonexistent_tool")

    def test_get_all_tools(self):
        tool1 = MockTool()
        tool2 = MockTool()
        tool2.name = "mock_tool2"
        self.tool_manager.register_tool(tool1)
        self.tool_manager.register_tool(tool2)
        tools = self.tool_manager.get_all_tools()
        self.assertEqual(len(tools), 2)
        self.assertIn(tool1, tools)
        self.assertIn(tool2, tools)


if __name__ == "__main__":
    unittest.main()
