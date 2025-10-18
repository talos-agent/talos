from __future__ import annotations

import importlib.metadata
import inspect
import logging

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class ToolManager:
    """
    A class for managing and discovering tools for the Talos agent.
    """

    def __init__(self) -> None:
        self.tools: dict[str, BaseTool] = {}
        self._discover_tools()

    def _discover_tools(self) -> None:
        """
        Discovers tools via entry points.
        """
        entry_points = importlib.metadata.entry_points(group="talos.tools")
        for entry_point in entry_points:
            try:
                tool_cls_or_factory = entry_point.load()
                if inspect.isclass(tool_cls_or_factory) and issubclass(tool_cls_or_factory, BaseTool):
                    tool_instance = tool_cls_or_factory()
                    self.register_tool(tool_instance)
                elif callable(tool_cls_or_factory):
                    tool_instance = tool_cls_or_factory()
                    if isinstance(tool_instance, BaseTool):
                        self.register_tool(tool_instance)
                    else:
                        logger.warning(f"Factory {entry_point.name} did not return a BaseTool instance.")
                else:
                    logger.warning(f"Entry point {entry_point.name} is not a class or a factory.")

            except Exception as e:
                logger.error(f"Failed to load tool from entry point {entry_point.name}: {e}")

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
