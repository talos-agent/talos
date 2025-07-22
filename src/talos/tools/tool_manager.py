from __future__ import annotations

from langchain_core.tools import BaseTool


class ToolManager:
    """
    A class for managing and discovering tools for the Talos agent.
    """

    def __init__(self) -> None:
        self.tools: dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool) -> None:
        """
        Registers a tool with the ToolManager.
        """
        if tool.name in self.tools:
            raise ValueError(f"Tool with name '{tool.name}' already registered.")
        self.tools[tool.name] = tool

    def unregister_tool(self, tool_name: str) -> None:
        """
        Unregisters a tool from the ToolManager.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool with name '{tool_name}' not found.")
        del self.tools[tool_name]

    def get_tool(self, tool_name: str) -> BaseTool:
        """
        Gets a tool by name.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool with name '{tool_name}' not found.")
        return self.tools[tool_name]

    def get_all_tools(self) -> list[BaseTool]:
        """
        Gets all registered tools.
        """
        return list(self.tools.values())
