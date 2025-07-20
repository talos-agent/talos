from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Optional

from langchain_core.tools import BaseTool

from talos.tools.supervised_tool import SupervisedTool

if TYPE_CHECKING:
    from talos.hypervisor.supervisor import Supervisor


class ToolManager:
    """
    A class for managing and discovering tools for the Talos agent.
    """

    def __init__(self, supervisor: Optional["Supervisor"] = None):
        self.tools: Dict[str, BaseTool] = {}
        self.supervisor = supervisor

    def register_tool(self, tool: BaseTool):
        """
        Registers a tool with the ToolManager.
        """
        if tool.name in self.tools:
            raise ValueError(f"Tool with name '{tool.name}' already registered.")
        self.tools[tool.name] = tool

    def unregister_tool(self, tool_name: str):
        """
        Unregisters a tool from the ToolManager.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool with name '{tool_name}' not found.")
        del self.tools[tool_name]

    def get_tool(self, tool_name: str, messages: Optional[list] = None) -> BaseTool:
        """
        Gets a tool by name.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool with name '{tool_name}' not found.")
        tool = self.tools[tool_name]
        if self.supervisor:
            return SupervisedTool(
                name=tool.name,
                description=tool.description,
                args_schema=tool.args_schema,
                tool=tool,
                supervisor=self.supervisor,
                messages=messages or [],
            )
        return tool

    def get_all_tools(self) -> List[BaseTool]:
        """
        Gets all registered tools.
        """
        return list(self.tools.values())
