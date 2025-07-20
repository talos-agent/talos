from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from talos.core.agent import Agent


class Supervisor(ABC):
    """
    An abstract base class for supervisors.
    """

    @abstractmethod
    def set_agent(self, agent: "Agent"):
        """
        Sets the agent to be supervised.
        """
        pass

    @abstractmethod
    def approve(self, messages: list, action: str, args: dict) -> bool:
        """
        Approves or denies an action.
        """
        pass
