from abc import ABC, abstractmethod
from typing import Any

from talos.services.abstract.service import Service


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

    @abstractmethod
    def get_user_timeline(self, username: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def get_user_mentions(self, username: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def get_tweet(self, tweet_id: str, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def search(self, query: str, **kwargs: Any) -> Any:
        pass


class TwitterPersona(Service, ABC):
    """
    An abstract base class for a Twitter persona service.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the service.
        """
        pass
