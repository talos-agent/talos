from abc import ABC, abstractmethod

from eth_rpc import PrivateKeyWallet
from pydantic import BaseModel


class Strategy(BaseModel, ABC):
    name: str
    wallet_id: str | None = None

    @abstractmethod
    async def check(self) -> bool:
        """check if an update is needed"""
        ...

    @abstractmethod
    async def update(self) -> bool:
        """update the strategy"""
        ...

    def get_wallet(self) -> PrivateKeyWallet:
        """get the wallet"""
        ...
