from typing import Any

from eth_rpc.networks import Arbitrum

from talos.constants import OHM, WETH
from talos.contracts.camelot_swap import CamelotYakSwap
from talos.core.scheduled_job import ScheduledJob
from talos.database.models import Swap
from talos.database.session import get_session
from talos.utils import RoflClient


class TwapOHMJob(ScheduledJob):
    STRATEGY_ID = "ohm_buyer"
    WALLET_ID = "Talos.ohm_strategy"
    client: RoflClient

    def __init__(self, **kwargs):
        super().__init__(
            name="olympus_strategy",
            description="Olympus strategy",
            cron_expression="*/15 * * * *",
        )
        self.client = RoflClient()

    async def run(self, **kwargs: Any) -> Any:
        wallet = await self.client.get_wallet(self.WALLET_ID)
        wallet_balance = await wallet.balance()
        swap_amount = min(wallet_balance, int(1e14))
        if wallet_balance < int(1e14):
            return

        tx_hash, transfer_event = await CamelotYakSwap.swap_for_ohm(
            amount_in=swap_amount,
            wallet=wallet,
        )

        with get_session() as session:
            swap = Swap(
                strategy_id=self.STRATEGY_ID,
                tx_hash=tx_hash,
                chain_id=Arbitrum.chain_id,
                wallet_address=wallet.address,
                amount_in=swap_amount,
                token_in=WETH.ARBITRUM,
                amount_out=transfer_event.amount,
                token_out=OHM.ARBITRUM,
            )
            session.add(swap)
            session.commit()
