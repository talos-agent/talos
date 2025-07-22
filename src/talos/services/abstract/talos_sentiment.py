from abc import ABC, abstractmethod

from talos.services.base import Service


class TalosSentiment(Service, ABC):
    """
    An abstract base class for a Talos sentiment service.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the service.
        """
        pass
