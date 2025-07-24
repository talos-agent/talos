from __future__ import annotations

from typing import TYPE_CHECKING, Any

from talos.hypervisor.supervisor import Supervisor, AsyncSupervisor

if TYPE_CHECKING:
    from talos.core.agent import Agent


class SimpleSupervisor(Supervisor):
    """
    A simple supervisor that approves every other tool call.
    """

    counter: int = 0

    def set_agent(self, agent: "Agent"):
        """
        Sets the agent to be supervised.
        """
        pass

    def approve(self, action: str, args: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Approves or denies an action.
        """
        self.counter += 1
        if self.counter % 2 == 0:
            return True, None
        return False, "Denied by SimpleSupervisor"


class AsyncSimpleSupervisor(AsyncSupervisor):
    """
    A simple async supervisor that approves every other tool call.
    """

    counter: int = 0

    def set_agent(self, agent: "Agent"):
        """
        Sets the agent to be supervised.
        """
        pass

    async def approve_async(self, action: str, args: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Approves or denies an action asynchronously.
        """
        self.counter += 1
        if self.counter % 2 == 0:
            return True, None
        return False, "Denied by AsyncSimpleSupervisor"
