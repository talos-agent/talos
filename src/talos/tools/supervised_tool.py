from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool

from talos.hypervisor.supervisor import Supervisor


class SupervisedTool(BaseTool):
    """
    A tool that is supervised by a hypervisor.
    """

    tool: BaseTool
    supervisor: Supervisor | None = None
    messages: list

    def set_supervisor(self, supervisor: Supervisor | None):
        """
        Sets the supervisor for the tool.
        """
        self.supervisor = supervisor

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Runs the tool.
        """
        tool_input = args[0] if args else kwargs
        if self.supervisor:
            approved, error_message = self.supervisor.approve(self.name, tool_input)
            if approved:
                return self.tool.run(tool_input, **kwargs)
            else:
                return error_message or f"Tool call to '{self.name}' denied by supervisor."
        return self.tool.run(tool_input, **kwargs)
