import logging
from typing import Optional

import numpy as np
from eth_rpc import Block, PrivateKeyWallet
from eth_rpc.networks import Arbitrum
from eth_rpc.types import primitives
from eth_rpc.utils import to_checksum
from hexbytes import HexBytes
from eth_typing import HexStr, HexAddress
from pydantic import BaseModel, Field, PrivateAttr

from ..constants import SYNTHETICS_ROUTER_CONTRACT_ADDRESS, ORDER_VAULT_ADDRESS, USDC_ADDRESS, WETH_ADDRESS, DATASTORE_ADDRESS
from ..contracts.exchange_router import CreateOrderParams, CreateOrderParamsAddresses, CreateOrderParamsNumbers, ExchangeRouter, exchange_router
from ..contracts.synthetics_reader import ExecutionPriceParams, PriceProps
from ..constants import PRECISION
from ..getters.markets import Markets
from ..getters.prices import OraclePrices
from ..utils.gas import get_execution_fee
from ..types import OrderType, DecreasePositionSwapType
from ..types.gas_limits import GasLimits
from ..utils.approval import check_if_approved
from ..utils.price import get_execution_price_and_price_impact


class Order(BaseModel):
    wallet: PrivateKeyWallet
    market_key: str
    collateral_address: str
    index_token_address: str
    is_long: bool
    size_delta: int
    initial_collateral_delta: int
    slippage_percent: float
    swap_path: list[HexAddress]
    max_fee_per_gas: int = Field(default=None)
    auto_cancel: bool = Field(default=False)
    debug_mode: bool = Field(default=False)
    execution_buffer: float = Field(default=1.3)
    markets: Markets = Field(default_factory=Markets)

    _exchange_router: ExchangeRouter = PrivateAttr(default=exchange_router)
    _is_swap: bool = PrivateAttr(default=False)
    _gas_limits: Optional[GasLimits] = PrivateAttr(default=None)
    _gas_limits_order_type: primitives.uint256 = PrivateAttr(default=None)

    async def get_block_fee(self):
        if self.max_fee_per_gas is None:
            block = await Block[Arbitrum].latest()
            self.max_fee_per_gas = block.base_fee_per_gas * 1.35

    async def determine_gas_limits(self):
        pass

    async def check_for_approval(self):
        """
        Check for Approval
        """
        await check_if_approved(
            self.wallet,
            SYNTHETICS_ROUTER_CONTRACT_ADDRESS,
            self.collateral_address,
            self.initial_collateral_delta,
            approve=True
        )

    async def _submit_transaction(
        self,
        wallet: PrivateKeyWallet,
        value_amount: float,
        multicall_args: list[bytes],
    ) -> HexStr:
        """
        Submit Transaction
        """
        logging.info("Building transaction...")

        tx_hash = await self._exchange_router.multicall(
            multicall_args
        ).execute(wallet, value=value_amount)

        logging.info("Txn submitted!")
        logging.info(
            "Check status: https://arbiscan.io/tx/0x{}".format(tx_hash)
        )
        logging.info("Transaction submitted!")

        return tx_hash

    def _get_prices(
        self,
        decimals: float,
        prices: float,
        is_open: bool = False,
        is_close: bool = False,
    ) -> tuple[float, int, float]:
        """
        Get Prices
        """
        logging.info("Getting prices...")
        price = np.median(
            [
                float(prices[self.index_token_address]['maxPriceFull']),
                float(prices[self.index_token_address]['minPriceFull'])
            ]
        )

        # Depending on if open/close & long/short, we need to account for
        # slippage in a different way
        if is_open:
            if self.is_long:
                slippage = str(
                    int(float(price) + float(price) * self.slippage_percent)
                )
            else:
                slippage = str(
                    int(float(price) - float(price) * self.slippage_percent)
                )
        elif is_close:
            if self.is_long:
                slippage = str(
                    int(float(price) - float(price) * self.slippage_percent)
                )
            else:
                slippage = str(
                    int(float(price) + float(price) * self.slippage_percent)
                )
        else:
            slippage = 0

        acceptable_price_in_usd = (
            int(slippage) * 10 ** (decimals - PRECISION)
        )

        logging.info(
            "Mark Price: ${:.4f}".format(price * 10 ** (decimals - PRECISION))
        )

        if acceptable_price_in_usd != 0:
            logging.info(
                "Acceptable price: ${:.4f}".format(acceptable_price_in_usd)
            )

        return price, int(slippage), acceptable_price_in_usd

    async def execute_order(self, is_open=False, is_close=False, is_swap=False) -> HexStr:
        """
        Create Order
        """

        await self.determine_gas_limits()
        block = await Block[Arbitrum].latest()
        gas_price = block.base_fee_per_gas
        execution_fee = int(
            get_execution_fee(
                self._gas_limits,
                self._gas_limits_order_type,
                gas_price
            )
        )

        # Dont need to check approval when closing
        if not is_close and not self.debug_mode:
            await self.check_for_approval()

        execution_fee = int(execution_fee * self.execution_buffer)

        await self.markets.load_info()
        market_info = self.markets.info
        initial_collateral_delta_amount = self.initial_collateral_delta
        prices = await OraclePrices(chain=Arbitrum).get_recent_prices()
        size_delta_price_price_impact = self.size_delta

        # when decreasing size delta must be negative
        if is_close:
            size_delta_price_price_impact = size_delta_price_price_impact * -1

        callback_gas_limit = 0
        min_output_amount = 0

        if is_open:
            order_type = OrderType.MarketIncrease
        elif is_close:
            order_type = OrderType.MarketDecrease
        elif is_swap:
            order_type = OrderType.MarketSwap

            # Estimate amount of token out using a reader function, necessary
            # for multi swap
            estimated_output = self.estimated_swap_output(
                market_info[self.swap_path[0]],
                self.collateral_address,
                initial_collateral_delta_amount
            )

            # this var will help to calculate the cost gas depending on the
            # operation
            self._get_limits_order_type = self._gas_limits['single_swap']
            if len(self.swap_path) > 1:
                estimated_output = self.estimated_swap_output(
                    market_info[self.swap_path[1]],
                    USDC_ADDRESS,
                    int(
                        estimated_output[
                            "out_token_amount"
                        ] - estimated_output[
                            "out_token_amount"
                        ] * self.slippage_percent
                    )
                )
                self._get_limits_order_type = self._gas_limits['swap_order']

            min_output_amount = estimated_output["out_token_amount"] - \
                estimated_output["out_token_amount"] * self.slippage_percent

        decrease_position_swap_type = DecreasePositionSwapType.NoSwap

        should_unwrap_native_token = True
        referral_code = HexBytes(
            "0x0000000000000000000000000000000000000000000000000000000000000000"
        )
        user_wallet_address = self.wallet.address
        eth_zero_address = HexAddress(HexStr("0x0000000000000000000000000000000000000000"))
        ui_ref_address = HexAddress(HexStr("0x0000000000000000000000000000000000000000"))
        gmx_market_address = to_checksum(self.market_key)

        # parameters using to calculate execution price
        execution_price_parameters = ExecutionPriceParams(
            data_store=DATASTORE_ADDRESS,
            market_key=self.market_key,
            index_token_price=PriceProps(
                min=int(prices[self.index_token_address]['maxPriceFull']),
                max=int(prices[self.index_token_address]['minPriceFull'])
            ),
            position_size_in_usd=0,
            position_size_in_tokens=0,
            size_delta_usd=size_delta_price_price_impact,
            is_long=self.is_long
        )
        decimals = market_info[self.market_key]['market_metadata']['decimals']

        price, acceptable_price, acceptable_price_in_usd = self._get_prices(
            decimals,
            prices,
            is_open,
            is_close,
        )

        mark_price = 0

        # mark price should be actual price when opening
        if is_open:
            mark_price = int(price)

        # Market address and acceptable price not important for swap
        if is_swap:
            acceptable_price = 0
            gmx_market_address = "0x0000000000000000000000000000000000000000"

        execution_price_and_price_impact_dict = await get_execution_price_and_price_impact(
            execution_price_parameters,
            decimals,
        )
        logging.info(
            "Execution price: ${:.4f}".format(
                execution_price_and_price_impact_dict['execution_price']
            )
        )

        # Prevent txn from being submitted if execution price falls outside acceptable
        if is_open:
            if self.is_long:
                if execution_price_and_price_impact_dict[
                        'execution_price'] > acceptable_price_in_usd:
                    raise Exception("Execution price falls outside acceptable price!")
            elif not self.is_long:
                if execution_price_and_price_impact_dict[
                        'execution_price'] < acceptable_price_in_usd:
                    raise Exception("Execution price falls outside acceptable price!")
        elif is_close:
            if self.is_long:
                if execution_price_and_price_impact_dict[
                        'execution_price'] < acceptable_price_in_usd:
                    raise Exception("Execution price falls outside acceptable price!")
            elif not self.is_long:
                if execution_price_and_price_impact_dict[
                        'execution_price'] > acceptable_price_in_usd:
                    raise Exception("Execution price falls outside acceptable price!")

        user_wallet_address = to_checksum(
            user_wallet_address
        )

        cancellation_receiver = user_wallet_address

        eth_zero_address = to_checksum(
            eth_zero_address
        )
        ui_ref_address = to_checksum(
            ui_ref_address
        )
        collateral_address = to_checksum(
            self.collateral_address
        )

        auto_cancel = self.auto_cancel

        arguments = CreateOrderParams(
            addresses=CreateOrderParamsAddresses(
                receiver=user_wallet_address,
                cancellation_receiver=cancellation_receiver,
                callback_contract=eth_zero_address,
                ui_fee_receiver=ui_ref_address,
                market=gmx_market_address,
                initial_collateral_token=collateral_address,
                swap_path=self.swap_path,
            ),
            numbers=CreateOrderParamsNumbers(
                size_delta_usd=self.size_delta,
                initial_collateral_delta_amount=self.initial_collateral_delta,
                trigger_price=mark_price,
                acceptable_price=acceptable_price,
                execution_fee=execution_fee,
                callback_gas_limit=callback_gas_limit,
                min_output_amount=int(min_output_amount),
                valid_from_time=0,
            ),
            order_type=order_type,
            decrease_position_swap_type=decrease_position_swap_type,
            is_long=self.is_long,
            should_unwrap_native_token=should_unwrap_native_token,
            auto_cancel=auto_cancel,
            referral_code=referral_code,
            data_list=[],
        )

        print("ARGUMENTS", arguments)

        # If the collateral is not native token (ie ETH/Arbitrum or AVAX/AVAX)
        # need to send tokens to vault

        value_amount = execution_fee
        if self.collateral_address != WETH_ADDRESS and not is_close:
            multicall_args = [
                HexBytes(self._send_wnt(value_amount)),
                HexBytes(
                    self._send_tokens(
                        self.collateral_address,
                        initial_collateral_delta_amount
                    )
                ),
                HexBytes(self._create_order(arguments))
            ]
        else:
            # send start token and execute fee if token is ETH or AVAX
            if is_open or is_swap:
                value_amount = initial_collateral_delta_amount + execution_fee

            multicall_args = [
                HexBytes(self._send_wnt(value_amount)),
                HexBytes(self._create_order(arguments))
            ]
            print("MULTICALL ARGS", multicall_args)

        return await self._submit_transaction(
            self.wallet,
            value_amount,
            multicall_args,
        )

    def _create_order(self, params: CreateOrderParams) -> primitives.bytes32:
        """
        Create Order
        """
        return bytes.fromhex(self._exchange_router.create_order(
            params
        ).data[2:])

    def _send_tokens(self, amount: primitives.uint256) -> HexStr:
        """
        Send tokens
        """
        return bytes.fromhex(self._exchange_router.send_tokens(
            (
                self.collateral_address,
                ORDER_VAULT_ADDRESS,
                amount
            ),
        ).data[2:])

    def _send_wnt(self, amount: primitives.uint256) -> HexStr:
        """
        Send WNT
        """
        return bytes.fromhex(self._exchange_router.send_wnt(
            (
                ORDER_VAULT_ADDRESS,
                amount
            )
        ).data[2:])
