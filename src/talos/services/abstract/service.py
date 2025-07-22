from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class Service(BaseModel, ABC):
    """
    An abstract base class for a service.
    Services are a way to organize and manage the agent's actions.
    They are LLM driven actions, which means that they are powered by a
    language model. This allows them to be more flexible and powerful
    than traditional tools.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the service.
        """
        pass
