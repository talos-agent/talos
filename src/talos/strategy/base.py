from abc import ABC, abstractmethod

from pydantic import BaseModel


class Strategy(BaseModel, ABC):
    name: str

    @abstractmethod
    async def check(self) -> bool:
        """check if an update is needed"""
        ...

    @abstractmethod
    async def update(self) -> bool:
        """update the strategy"""
        ...
