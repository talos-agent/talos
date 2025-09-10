from typing import Annotated

from eth_rpc import ContractFunc, PrivateKeyWallet, ProtocolBase, TransactionReceipt
from eth_rpc.networks import Arbitrum
from eth_rpc.types import METHOD, Name, Struct, primitives
from eth_rpc.utils import EventReceiptUtility
from eth_typeshed.erc20 import TransferEvent, TransferEventType
from eth_typing import HexStr
from pydantic import BaseModel

from talos.constants import OHM, WETH, CamelotYakSwapConstants


class Trade(Struct):
    amount_in: primitives.uint256
    amount_out: primitives.uint256
    path: list[primitives.address]
    adapters: list[primitives.address]
    recipients: list[primitives.address]


class Request(BaseModel):
    trade: Trade
    fee: primitives.uint256
    to: primitives.address


class QueryAdapterArgs(BaseModel):
    amount_in: primitives.uint256
    token_in: primitives.address
    token_out: primitives.address
    index: primitives.uint8


class QueryAdapterResponse(BaseModel):
    amount_out: primitives.uint256
    pool_address: primitives.address


class CamelotYakSwap(ProtocolBase):
    swap_no_split_from_eth: Annotated[ContractFunc[Request, None], Name("swapNoSplitFromETH")] = METHOD
    ADAPTERS: ContractFunc[primitives.uint256, primitives.address] = METHOD
    query_adapter: Annotated[ContractFunc[QueryAdapterArgs, QueryAdapterResponse], Name("queryAdapter")] = METHOD

    @classmethod
    def OHM_PATH(cls) -> list[primitives.address]:
        return [WETH.ARBITRUM, OHM.ARBITRUM]

    @classmethod
    async def swap_for_ohm(
        self,
        amount_in: primitives.uint256,
        wallet: PrivateKeyWallet,
    ) -> tuple[HexStr, TransferEventType]:
        router = CamelotYakSwap[Arbitrum](address=CamelotYakSwapConstants.ROUTER)

        query_response = await router.query_adapter(
            QueryAdapterArgs(
                amount_in=amount_in,
                token_in=WETH.ARBITRUM,
                token_out=OHM.ARBITRUM,
                index=0,
            )
        ).get()

        path = self.OHM_PATH()
        adapters = [CamelotYakSwapConstants.ADAPTER]
        recipients = [query_response.pool_address]
        request = Request(
            trade=Trade(
                amount_in=amount_in,
                amount_out=int(query_response.amount_out * 99 / 100),
                path=path,
                adapters=adapters,
                recipients=recipients,
            ),
            fee=0,
            to=wallet.address,
        )

        tx_hash = await router.swap_no_split_from_eth(request).execute(wallet, value=amount_in)

        await TransactionReceipt[Arbitrum].wait_until_finalized(tx_hash, timeout=10)

        receipt = await TransactionReceipt[Arbitrum].get_by_hash(tx_hash)
        transfers = await EventReceiptUtility.get_events_from_receipt([TransferEvent], receipt)

        received_events: list[TransferEventType] = []
        sent_events = []
        for transfer in transfers:
            if (
                transfer.event.recipient.lower() == wallet.address.lower()
                and transfer.log.address.lower() == OHM.ARBITRUM.lower()
            ):
                received_events.append(transfer.event)
            if transfer.event.sender.lower() == wallet.address.lower():
                sent_events.append(transfer.event)

        received_event = received_events[0]
        return (tx_hash, received_event)
