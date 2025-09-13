from enum import IntEnum, StrEnum
from typing import Annotated

import httpx
from eth_abi import encode
from eth_rpc import ContractFunc, PrivateKeyWallet, ProtocolBase, TransactionReceipt
from eth_rpc.networks import Arbitrum, Ethereum
from eth_rpc.types import METHOD, Name, Network, Struct, primitives
from eth_typeshed.erc20 import ApproveRequest, OwnerSpenderRequest
from eth_typeshed.weth import WETH
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel

from .schema import CCIPMessageResponse, CCIPMessageStatusResponse

ZERO_ADDRESS = HexAddress(HexStr("0x0000000000000000000000000000000000000000"))
EVM_EXTRA_ARGS_V1_TAG = "0x97a657c9"


class WETH_ADDRESS(StrEnum):
    ARBITRUM = HexAddress(HexStr("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"))
    ETHEREUM = HexAddress(HexStr("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"))

    @classmethod
    def from_network(cls, network: type[Network]) -> HexAddress:
        if network == Arbitrum:
            return HexAddress(HexStr(cls.ARBITRUM))
        elif network == Ethereum:
            return HexAddress(HexStr(cls.ETHEREUM))
        raise ValueError(f"Invalid network: {network}")


class CCIPRouterAddress(StrEnum):
    ARBITRUM = HexAddress(HexStr("0x141fa059441E0ca23ce184B6A78bafD2A517DdE8"))
    ETHEREUM = HexAddress(HexStr("0x80226fc0Ee2b096224EeAc085Bb9a8cba1146f7D"))

    @classmethod
    def from_network(cls, network: type[Network]) -> HexAddress:
        if network == Arbitrum:
            return HexAddress(HexStr(cls.ARBITRUM))
        elif network == Ethereum:
            return HexAddress(HexStr(cls.ETHEREUM))
        raise ValueError(f"Invalid network: {network}")


class CCIPConstants(IntEnum):
    ARBITRUM = 4949039107694359620
    MAINNET = 5009297550715157269

    @classmethod
    def from_network(cls, network: type[Network]) -> primitives.uint64:
        if network == Arbitrum:
            return primitives.uint64(cls.ARBITRUM)
        elif network == Ethereum:
            return primitives.uint64(cls.MAINNET)
        raise ValueError(f"Invalid network: {network}")


class EVMTokenAmount(Struct):
    token: HexAddress
    amount: primitives.uint256


class EVM2AnyMessage(Struct):
    receiver: bytes
    data: bytes
    token_amounts: list[EVMTokenAmount]
    fee_token: HexAddress
    extra_args: bytes


class CCIPSendArgs(BaseModel):
    dest_chain_selector: primitives.uint64
    message: EVM2AnyMessage


class CCIPFeeArgs(BaseModel):
    dest_chain_selector: primitives.uint64
    message: EVM2AnyMessage


class CCIPRouter(ProtocolBase):
    get_fee: Annotated[ContractFunc[CCIPFeeArgs, primitives.uint256], Name("getFee")] = METHOD
    ccip_send: Annotated[ContractFunc[CCIPSendArgs, primitives.bytes32], Name("ccipSend")] = METHOD

    @classmethod
    def _encode_address(self, address: HexAddress) -> bytes:
        address_hex: bytes = encode(["address"], [address])
        return address_hex

    @classmethod
    def _encode_gas_limit(self, gas_limit: primitives.uint256) -> bytes:
        prefix = EVM_EXTRA_ARGS_V1_TAG[2:]
        gas_limit_bytes = gas_limit.to_bytes(32, "big").hex()
        return bytes.fromhex(f"{prefix}{gas_limit_bytes}")

    async def bridge_native(
        self,
        amount: primitives.uint256,
        wallet: PrivateKeyWallet,
        from_network: type[Network],
        to_network: type[Network],
        gas_limit: primitives.uint256 = primitives.uint256(200_000),
        recipient: HexAddress | None = None,
        verbose: bool = False,
        wrap: bool = True,
    ) -> HexStr:
        weth_address = WETH_ADDRESS.from_network(from_network)
        weth_contract = WETH[from_network](address=weth_address)
        if wrap:
            tx_hash = await weth_contract.deposit().execute(wallet, value=amount)

            await TransactionReceipt[from_network].wait_until_finalized(tx_hash, timeout=10)

            if verbose:
                print(f"WETH deposit tx hash: {tx_hash}")

        if not recipient:
            recipient = wallet.address

        allowance = await weth_contract.allowance(OwnerSpenderRequest(owner=wallet.address, spender=self.address)).get()
        if allowance < amount:
            tx_hash = await weth_contract.approve(ApproveRequest(spender=self.address, amount=amount)).execute(wallet)

            await TransactionReceipt[from_network].wait_until_finalized(tx_hash, timeout=10)

            if verbose:
                print(f"WETH approve tx hash: {tx_hash}")

        dest_chain_selector = CCIPConstants.from_network(to_network)
        message = EVM2AnyMessage(
            receiver=self._encode_address(recipient),
            data=b"",
            token_amounts=[EVMTokenAmount(token=weth_address, amount=amount)],
            extra_args=self._encode_gas_limit(gas_limit),
            fee_token=ZERO_ADDRESS,
        )
        fee_amount = await self.get_fee(CCIPFeeArgs(dest_chain_selector=dest_chain_selector, message=message)).get()

        return HexStr(
            await self.ccip_send(CCIPSendArgs(dest_chain_selector=dest_chain_selector, message=message)).execute(
                wallet, value=fee_amount
            )
        )

    async def find_message_id(self, tx_hash: HexStr) -> HexStr | None:
        CCIP_EXPLORER_QUERY_URL = "https://ccip.chain.link/api/h/atlas/search?msgIdOrTxnHash="

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CCIP_EXPLORER_QUERY_URL}{tx_hash}")
        if response.status_code != 200:
            raise Exception(f"Failed to get CCIP message status: {response.status_code}")

        status_response = CCIPMessageStatusResponse.model_validate(response.json())

        if status_response.transaction_hash:
            return status_response.transaction_hash[0].message_id
        return None

    async def check_status(self, tx_hash: HexStr) -> CCIPMessageResponse:
        CCIP_EXPLORER_URL = "https://ccip.chain.link/api/h/atlas/message/"

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CCIP_EXPLORER_URL}{tx_hash}")
        if response.status_code != 200:
            raise Exception(f"Failed to get CCIP message status: {response.status_code}")
        return CCIPMessageResponse.model_validate(response.json())
