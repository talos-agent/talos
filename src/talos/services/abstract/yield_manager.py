from abc import ABC, abstractmethod


class YieldManager(ABC):
    @abstractmethod
    def update_staking_apr(self) -> float:
        pass
