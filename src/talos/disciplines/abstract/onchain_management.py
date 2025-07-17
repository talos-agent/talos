from abc import ABC, abstractmethod


class OnChainManagement(ABC):
    """
    An abstract base class for on-chain management.
    """

    @abstractmethod
    def get_treasury_balance(self) -> float:
        """
        Gets the balance of the treasury.
        """
        pass

    @abstractmethod
    def add_to_vault(self, vault_address: str, token: str, amount: float) -> None:
        """
        Adds funds to a vault.
        """
        pass

    @abstractmethod
    def remove_from_vault(self, vault_address: str, amount: float) -> None:
        """
        Removes funds from a vault.
        """
        pass

    @abstractmethod
    def deploy_vault(self) -> str:
        """
        Deploys a new vault contract.
        """
        pass
