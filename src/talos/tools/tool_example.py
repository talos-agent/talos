from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

from langchain_core.tools import tool

from talos.hypervisor.supervisor import Supervisor

if TYPE_CHECKING:
    from talos.core.agent import Agent


@tool
def get_current_time() -> str:
    """
    Returns the current time.
    """
    return datetime.datetime.now().isoformat()


class SimpleSupervisor(Supervisor):
    """
    A simple supervisor that approves every other tool call.
    """

    def __init__(self):
        self.counter = 0

    def set_agent(self, agent: "Agent"):
        """
        Sets the agent to be supervised.
        """
        pass

    def approve(self, messages: list, action: str, args: dict[str, Any]) -> bool:
        """
        Approves or denies an action.
        """
        self.counter += 1
        return self.counter % 2 != 0
