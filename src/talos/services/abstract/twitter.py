from abc import ABC, abstractmethod

from talos.services.base import Service


class Twitter(Service, ABC):
    """
    An abstract base class for a Twitter service.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the service.
        """
        pass
