from __future__ import annotations

from abc import ABC, abstractmethod


class Supervisor(ABC):
    """
    An abstract base class for supervisors.
    """

    @abstractmethod
    def approve(self, messages: list, action: str, args: dict) -> bool:
        """
        Approves or denies an action.
        """
        pass
