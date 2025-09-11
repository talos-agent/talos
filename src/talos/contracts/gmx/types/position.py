from __future__ import annotations

from eth_rpc import PrivateKeyWallet
from eth_rpc.types import primitives
from eth_typing import ChecksumAddress, HexAddress, HexStr
from pydantic import BaseModel

from ..constants import WETH_ADDRESS
from ..contracts import datastore, exchange_router
from ..getters.prices import OraclePrices
from ..types.orders import OrderType
from ..utils.keys import claimable_funding_amount_key
from ..utils.tokens import get_tokens_address_dict
from .markets import Market


class Position(BaseModel):
    """
    Get all open positions for a given address on the chain defined in
    class init

    Parameters
    ----------
    address : HexAddress
        The address of the account to get the positions for

    Returns
    -------
    list[Position]
        A list of Position objects

    > positions = await Position.get_positions(address)
    > await positions[0].update_leverage(wallet, 1)

    """

    account: HexAddress
    market: Market
    market_symbol: str
    collateral_token: ChecksumAddress
    position_size: float
    size_in_tokens: int
    entry_price: float
    initial_collateral_amount: int
    initial_collateral_amount_usd: float
    leverage: float
    borrowing_factor: float
    funding_fee_amount_per_size: float
    long_token_claimable_funding_amount_per_size: float
    short_token_claimable_funding_amount_per_size: float
    position_modified_at: str
    is_long: bool
    percent_profit: float
    mark_price: float

    @classmethod
    async def get_positions(cls, address: ChecksumAddress) -> list[Position]:
        from ..getters.open_positions import GetOpenPositions

        positions = await GetOpenPositions(address=address).get_data()
        return list(positions.values())

    async def claim_market_fees(self, wallet: PrivateKeyWallet) -> HexStr | None:
        claimable_fee = await self.get_claimable_funding_fees()
        if claimable_fee > 0:
            tx_hash: HexStr = await exchange_router.claim_funding_fees(
                ([self.market.address], [self.collateral_token], [wallet.address])
            ).execute(wallet)
            return tx_hash
        return None

    async def get_claimable_funding_fees(self) -> primitives.uint256:
        claimable_fee = claimable_funding_amount_key(self.market.address, self.market.short_token_address, self.account)
        return primitives.uint256(await datastore.get_uint(claimable_fee).get())

    async def update_leverage(
        self,
        wallet: PrivateKeyWallet,
        new_leverage: float,
        additional_collateral: int = 0,
        slippage_percent: float = 0.003,
        swap_path: list[HexAddress] = [],
    ) -> HexStr | None:
        from ..order.executor import OrderExecutor

        position_size = self.position_size

        new_size: float = position_size * new_leverage / self.leverage
        size_delta = int(abs(new_size - self.position_size) * 1e30)

        if position_size < new_size:
            order_type = OrderType.MarketIncrease
        else:
            order_type = OrderType.MarketDecrease

        order = OrderExecutor(
            wallet=wallet,
            market_key=self.market.address,
            collateral_address=self.collateral_token,
            index_token_address=self.market.index_token_address,
            is_long=self.is_long,
            size_delta=size_delta,
            initial_collateral_delta=additional_collateral,
            slippage_percent=slippage_percent,
            swap_path=swap_path,
            execution_buffer=1.5,
            debug_mode=True,
        )

        tx_hash = await order.execute(order_type=order_type)
        return tx_hash

    async def close(
        self, wallet: PrivateKeyWallet, slippage_percent: float = 0.003, swap_path: list[HexAddress] = []
    ) -> HexStr | None:
        from ..order.executor import OrderExecutor

        order = OrderExecutor(
            wallet=wallet,
            market_key=self.market.address,
            collateral_address=self.collateral_token,
            index_token_address=self.market.index_token_address,
            is_long=self.is_long,
            size_delta=int(self.position_size * 10**30),
            initial_collateral_delta=self.size_in_tokens,
            slippage_percent=slippage_percent,
            swap_path=swap_path,
            execution_buffer=1.5,
        )

        tx_hash = await order.execute(order_type=OrderType.MarketDecrease)
        return tx_hash

    @classmethod
    async def create_position(
        cls,
        wallet: PrivateKeyWallet,
        market: Market,
        is_long: bool,
        size_in_usd: int,
        collateral_amount: int,
        slippage_percent: float = 0.003,
        swap_path: list[HexAddress] = [],
        collateral_address: ChecksumAddress = WETH_ADDRESS,
    ) -> HexStr | None:
        from ..order.executor import OrderExecutor

        prices = await OraclePrices().get_recent_prices()
        price = prices[collateral_address].max_price_full
        tokens = await get_tokens_address_dict()

        token_collateral_amount: float = float(collateral_amount / price)
        decimal: int = tokens[collateral_address].decimals
        oracle_factor: int = 12
        scaled_amount: int = int(token_collateral_amount * 10 ** (decimal + oracle_factor))

        order = OrderExecutor(
            wallet=wallet,
            market_key=market.address,
            collateral_address=collateral_address,
            index_token_address=market.index_token_address,
            is_long=is_long,
            size_delta=int(size_in_usd * 10**30),  # 10**30
            initial_collateral_delta=scaled_amount,  # amount of collateral to send
            slippage_percent=slippage_percent,
            swap_path=swap_path,
            execution_buffer=1.5,
            debug_mode=True,
        )

        tx_hash = await order.execute()
        return tx_hash
