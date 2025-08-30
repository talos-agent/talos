from talos.services.abstract.onchain_management import OnChainManagement
from talos.services.implementations.talos_sentiment import TalosSentimentService
from talos.services.implementations.yield_manager import YieldManagerService


class OnChainManagementService(OnChainManagement):
    """
    A discipline for on-chain management.
    """

    def __init__(
        self,
        yield_manager: YieldManagerService,
        sentiment_service: "TalosSentimentService",
    ):
        self.yield_manager = yield_manager
        self.sentiment_service = sentiment_service

    def get_treasury_balance(self) -> float:
        """
        Gets the balance of the treasury.
        """
        return 1000.0

    def add_to_vault(self, vault_address: str, token: str, amount: float) -> None:
        """
        Adds funds to a vault.
        """
        print(f"Adding {amount} of {token} to vault {vault_address}")

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

    def set_staking_apr(self) -> None:
        """
        Sets the staking APR.
        """
        sentiment = self.sentiment_service.analyze_sentiment(search_query="talos")
        if sentiment.score is not None:
            new_apr = self.yield_manager.update_staking_apr(sentiment.score, "\n".join(sentiment.answers))
            print(f"Setting staking APR to {new_apr}")

    def deploy_contract(self, bytecode: str, salt: str, chain_id: int, check_duplicates: bool = False) -> str:
        """
        Deploy a smart contract with optional duplicate checking.
        """
        from talos.tools.contract_deployment import ContractDeploymentTool

        tool = ContractDeploymentTool()
        result = tool._run_unsupervised(
            bytecode=bytecode, salt=salt, chain_id=chain_id, check_duplicates=check_duplicates
        )
        return result.contract_address

    def check_deployment_duplicate(self, bytecode: str, salt: str, chain_id: int) -> bool:
        """
        Check if a contract deployment would be a duplicate.
        """
        from talos.database.models import ContractDeployment
        from talos.database.session import get_session
        from talos.utils.contract_deployment import calculate_contract_signature

        signature = calculate_contract_signature(bytecode, salt)

        with get_session() as session:
            existing = (
                session.query(ContractDeployment)
                .filter(ContractDeployment.contract_signature == signature, ContractDeployment.chain_id == chain_id)
                .first()
            )

            return existing is not None
