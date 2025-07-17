from disciplines.onchain_management_abc import OnChainManagement


class OnChainManagementDiscipline(OnChainManagement):
    """
    A discipline for on-chain management.
    """

    def get_treasury_balance(self) -> float:
        """
        Gets the balance of the treasury.
        """
        return 1000.0

    def add_to_vault(self, vault_address: str, amount: float) -> None:
        """
        Adds funds to a vault.
        """
        print(f"Adding {amount} to vault {vault_address}")

    def remove_from_vault(self, vault_address: str, amount: float) -> None:
        """
        Removes funds from a vault.
        """
        print(f"Removing {amount} from vault {vault_address}")

    def deploy_vault(self) -> str:
        """
        Deploys a new vault contract.
        """
        return "0x1234567890"
