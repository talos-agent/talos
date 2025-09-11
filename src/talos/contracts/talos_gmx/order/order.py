import logging
from typing import Optional

import numpy as np
from eth_rpc import Block, PrivateKeyWallet
from eth_rpc.networks import Arbitrum
from eth_rpc.types import primitives
from eth_rpc.utils import to_checksum
from eth_typing import ChecksumAddress, HexAddress, HexStr
from hexbytes import HexBytes
from pydantic import BaseModel, Field, PrivateAttr

from ..constants import (
    DATASTORE_ADDRESS,
    ORDER_VAULT_ADDRESS,
    PRECISION,
    SYNTHETICS_ROUTER_CONTRACT_ADDRESS,
    USDC_ADDRESS,
    WETH_ADDRESS,
)
from ..contracts.exchange_router import (
    CreateOrderParams,
    CreateOrderParamsAddresses,
    CreateOrderParamsNumbers,
    ExchangeRouter,
    exchange_router,
)
from ..contracts.synthetics_reader import ExecutionPriceParams, PriceProps
from ..getters.markets import Markets
from ..getters.prices import OraclePrices
from ..types import DecreasePositionSwapType, Market, OraclePriceData, OrderType
from ..types.gas_limits import GasLimits
from ..utils.approval import check_if_approved
from ..utils.gas import get_execution_fee
from ..utils.price import get_execution_price_and_price_impact


class Order(BaseModel):
    wallet: PrivateKeyWallet
    market_key: ChecksumAddress
    collateral_address: ChecksumAddress
    index_token_address: ChecksumAddress
    is_long: bool
    size_delta: int
    initial_collateral_delta: int
    slippage_percent: float
    swap_path: list[HexAddress]
    max_fee_per_gas: int | None = Field(default=None)
    auto_cancel: bool = Field(default=False)
    debug_mode: bool = Field(default=False)
    execution_buffer: float = Field(default=1.3)
    markets: Markets = Field(default_factory=Markets)

    _exchange_router: ExchangeRouter = PrivateAttr(default=exchange_router)
    _is_swap: bool = PrivateAttr(default=False)
    _gas_limits: Optional[GasLimits] = PrivateAttr(default=None)
    _gas_limits_order_type: primitives.uint256 | None = PrivateAttr(default=None)

    async def get_block_fee(self) -> None:
        if self.max_fee_per_gas is None:
            block = await Block[Arbitrum].latest()
            assert block.base_fee_per_gas is not None
            self.max_fee_per_gas = int(block.base_fee_per_gas * 1.35)

    async def estimated_swap_output(self, market: Market, in_token: HexAddress, in_token_amount: int) -> dict:  # type: ignore
        raise NotImplementedError()

    async def determine_gas_limits(self) -> None:
        pass

    async def check_for_approval(self) -> None:
        """
        Check for Approval
        """
        await check_if_approved(
            self.wallet,
            SYNTHETICS_ROUTER_CONTRACT_ADDRESS,
            self.collateral_address,
            self.initial_collateral_delta,
            approve=True,
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

        tx_hash: HexStr = await self._exchange_router.multicall(multicall_args).execute(wallet, value=value_amount)

        logging.info("Txn submitted!")
        logging.info("Check status: https://arbiscan.io/tx/0x{}".format(tx_hash))
        logging.info("Transaction submitted!")

        return tx_hash

    def _get_prices(
        self,
        decimals: float,
        prices: dict[ChecksumAddress, OraclePriceData],
        is_open: bool = False,
        is_close: bool = False,
    ) -> tuple[float, int, float]:
        """
        Get Prices
        """
        logging.info("Getting prices...")
        price = np.median(
            [
                float(prices[self.index_token_address].max_price_full),
                float(prices[self.index_token_address].min_price_full),
            ]
        )

        # Depending on if open/close & long/short, we need to account for
        # slippage in a different way
        if is_open:
            if self.is_long:
                slippage = int(float(price) + float(price) * self.slippage_percent)
            else:
                slippage = int(float(price) - float(price) * self.slippage_percent)
        elif is_close:
            if self.is_long:
                slippage = int(float(price) - float(price) * self.slippage_percent)
            else:
                slippage = int(float(price) + float(price) * self.slippage_percent)
        else:
            slippage = 0

        acceptable_price_in_usd = slippage * 10 ** (decimals - PRECISION)

        logging.info("Mark Price: ${:.4f}".format(float(price * 10 ** (decimals - PRECISION))))

        if acceptable_price_in_usd != 0:
            logging.info("Acceptable price: ${:.4f}".format(acceptable_price_in_usd))

        return float(price), int(slippage), acceptable_price_in_usd

    async def execute_order(self, is_open: bool = False, is_close: bool = False, is_swap: bool = False) -> HexStr:
        """
        Create Order
        """
        # Prepare order execution
        execution_fee, market_info, prices, size_delta_price_price_impact = await self._prepare_order_execution(
            is_close
        )

        # Determine order type and handle swap-specific logic
        order_type, min_output_amount = await self._determine_order_type_and_swap_logic(
            is_open, is_close, is_swap, market_info, size_delta_price_price_impact
        )

        # Calculate prices and validate execution
        (
            price,
            acceptable_price,
            acceptable_price_in_usd,
            mark_price,
            gmx_market_address,
        ) = await self._calculate_and_validate_prices(
            is_open, is_close, is_swap, market_info, prices, size_delta_price_price_impact
        )

        # Create order parameters
        arguments = self._create_order_parameters(
            order_type, execution_fee, min_output_amount, mark_price, acceptable_price, gmx_market_address
        )

        # Build and submit transaction
        value_amount, multicall_args = self._build_transaction_arguments(
            is_open, is_close, is_swap, execution_fee, arguments
        )

        return await self._submit_transaction(
            self.wallet,
            value_amount,
            multicall_args,  # type: ignore
        )

    async def _prepare_order_execution(
        self, is_close: bool
    ) -> tuple[
        primitives.uint256,
        dict[ChecksumAddress, Market],
        dict[ChecksumAddress, OraclePriceData],
        primitives.int256,
    ]:
        """
        Prepare order execution by getting fees, checking approvals, and loading market data
        """
        execution_fee = await self._get_execution_fee()

        # Don't need to check approval when closing
        if not is_close and not self.debug_mode:
            await self.check_for_approval()

        await self.markets.load_info()

        market_info = self.markets.info
        prices = await OraclePrices().get_recent_prices()
        size_delta_price_price_impact = self.size_delta

        # when decreasing size delta must be negative
        if is_close:
            size_delta_price_price_impact = size_delta_price_price_impact * -1

        return execution_fee, market_info, prices, primitives.int256(size_delta_price_price_impact)

    async def _determine_order_type_and_swap_logic(
        self,
        is_open: bool,
        is_close: bool,
        is_swap: bool,
        market_info: dict[ChecksumAddress, Market],
        size_delta_price_price_impact: int,
    ) -> tuple[OrderType, int]:
        """
        Determine order type and handle swap-specific logic
        """
        min_output_amount = 0

        if is_open:
            order_type = OrderType.MarketIncrease
        elif is_close:
            order_type = OrderType.MarketDecrease
        elif is_swap:
            order_type = OrderType.MarketSwap

            # Estimate amount of token out using a reader function, necessary
            # for multi swap
            estimated_output = await self.estimated_swap_output(
                market_info[to_checksum(self.swap_path[0])], self.collateral_address, self.initial_collateral_delta
            )

            # this var will help to calculate the cost gas depending on the
            # operation
            assert self._gas_limits is not None

            self._get_limits_order_type = self._gas_limits.single_swap
            if len(self.swap_path) > 1:
                estimated_output = await self.estimated_swap_output(
                    market_info[to_checksum(self.swap_path[1])],
                    USDC_ADDRESS,
                    int(
                        estimated_output["out_token_amount"]
                        - estimated_output["out_token_amount"] * self.slippage_percent
                    ),
                )
                self._get_limits_order_type = self._gas_limits.swap_order

            min_output_amount = (
                estimated_output["out_token_amount"] - estimated_output["out_token_amount"] * self.slippage_percent
            )

        return order_type, min_output_amount

    async def _calculate_and_validate_prices(
        self,
        is_open: bool,
        is_close: bool,
        is_swap: bool,
        market_info: dict[ChecksumAddress, Market],
        prices: dict[ChecksumAddress, OraclePriceData],
        size_delta_price_price_impact: int,
    ) -> tuple[float, int, float, int, HexAddress]:
        """
        Calculate prices and validate execution price
        """
        # Create execution price parameters
        execution_price_parameters = ExecutionPriceParams(
            data_store=DATASTORE_ADDRESS,
            market_key=self.market_key,
            index_token_price=PriceProps(
                min=primitives.uint256(int(prices[self.index_token_address].max_price_full)),
                max=primitives.uint256(int(prices[self.index_token_address].min_price_full)),
            ),
            position_size_in_usd=primitives.uint256(0),
            position_size_in_tokens=primitives.uint256(0),
            size_delta_usd=primitives.int256(size_delta_price_price_impact),
            is_long=self.is_long,
        )
        decimals = market_info[self.market_key].market_metadata.decimals

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

        gmx_market_address = to_checksum(self.market_key)
        # Market address and acceptable price not important for swap
        if is_swap:
            acceptable_price = 0
            gmx_market_address = to_checksum("0x0000000000000000000000000000000000000000")

        # Get execution price and validate
        execution_price_and_price_impact_dict = await get_execution_price_and_price_impact(
            execution_price_parameters,
            decimals,
        )
        logging.info("Execution price: ${:.4f}".format(execution_price_and_price_impact_dict["execution_price"]))

        # Validate execution price
        self._validate_execution_price(
            is_open, is_close, execution_price_and_price_impact_dict, acceptable_price_in_usd
        )

        return price, acceptable_price, acceptable_price_in_usd, mark_price, gmx_market_address

    def _validate_execution_price(
        self, is_open: bool, is_close: bool, execution_price_dict: dict[str, float], acceptable_price_in_usd: float
    ) -> None:
        """
        Validate that execution price falls within acceptable range
        """
        execution_price = execution_price_dict["execution_price"]

        if is_open:
            self._validate_open_position_price(execution_price, acceptable_price_in_usd)
        elif is_close:
            self._validate_close_position_price(execution_price, acceptable_price_in_usd)

    def _validate_open_position_price(self, execution_price: float, acceptable_price_in_usd: float) -> None:
        """Validate execution price for opening positions"""
        if self.is_long and execution_price > acceptable_price_in_usd:
            raise Exception("Execution price falls outside acceptable price!")
        elif not self.is_long and execution_price < acceptable_price_in_usd:
            raise Exception("Execution price falls outside acceptable price!")

    def _validate_close_position_price(self, execution_price: float, acceptable_price_in_usd: float) -> None:
        """Validate execution price for closing positions"""
        if self.is_long and execution_price < acceptable_price_in_usd:
            raise Exception("Execution price falls outside acceptable price!")
        elif not self.is_long and execution_price > acceptable_price_in_usd:
            raise Exception("Execution price falls outside acceptable price!")

    def _create_order_parameters(
        self,
        order_type: OrderType,
        execution_fee: int,
        min_output_amount: int,
        mark_price: int,
        acceptable_price: int,
        gmx_market_address: HexAddress,
    ) -> CreateOrderParams:
        """
        Create order parameters
        """
        decrease_position_swap_type = DecreasePositionSwapType.NoSwap
        should_unwrap_native_token = True
        referral_code = HexBytes("0x0000000000000000000000000000000000000000000000000000000000000000")
        user_wallet_address = to_checksum(self.wallet.address)
        eth_zero_address = to_checksum(HexAddress(HexStr("0x0000000000000000000000000000000000000000")))
        ui_ref_address = to_checksum(HexAddress(HexStr("0x0000000000000000000000000000000000000000")))
        collateral_address = to_checksum(self.collateral_address)

        return CreateOrderParams(
            addresses=CreateOrderParamsAddresses(
                receiver=user_wallet_address,
                cancellation_receiver=user_wallet_address,
                callback_contract=eth_zero_address,
                ui_fee_receiver=ui_ref_address,
                market=gmx_market_address,
                initial_collateral_token=collateral_address,
                swap_path=self.swap_path,
            ),
            numbers=CreateOrderParamsNumbers(
                size_delta_usd=primitives.uint256(self.size_delta),
                initial_collateral_delta_amount=primitives.uint256(self.initial_collateral_delta),
                trigger_price=primitives.uint256(mark_price),
                acceptable_price=primitives.uint256(acceptable_price),
                execution_fee=primitives.uint256(execution_fee),
                callback_gas_limit=primitives.uint256(0),
                min_output_amount=primitives.uint256(min_output_amount),
                valid_from_time=primitives.uint256(0),
            ),
            order_type=primitives.uint8(order_type),
            decrease_position_swap_type=primitives.uint8(decrease_position_swap_type),
            is_long=self.is_long,
            should_unwrap_native_token=should_unwrap_native_token,
            auto_cancel=self.auto_cancel,
            referral_code=primitives.bytes32(referral_code),
            data_list=[],
        )

    def _build_transaction_arguments(
        self,
        is_open: bool,
        is_close: bool,
        is_swap: bool,
        execution_fee: primitives.uint256,
        arguments: CreateOrderParams,
    ) -> tuple[primitives.uint256, list[HexBytes]]:
        """
        Build multicall transaction arguments
        """
        value_amount = execution_fee
        initial_collateral_delta_amount = self.initial_collateral_delta

        if self.collateral_address != WETH_ADDRESS and not is_close:
            multicall_args = [
                HexBytes(self._send_wnt(value_amount)),
                HexBytes(self._send_tokens(primitives.uint256(initial_collateral_delta_amount))),
                HexBytes(self._create_order(arguments)),
            ]
        else:
            # send start token and execute fee if token is ETH or AVAX
            if is_open or is_swap:
                value_amount = primitives.uint256(initial_collateral_delta_amount + execution_fee)

            multicall_args = [HexBytes(self._send_wnt(value_amount)), HexBytes(self._create_order(arguments))]

        return value_amount, multicall_args

    def _create_order(self, params: CreateOrderParams) -> primitives.bytes32:
        """
        Create Order
        """
        return primitives.bytes32(bytes.fromhex(self._exchange_router.create_order(params).data[2:]))

    def _send_tokens(self, amount: primitives.uint256) -> primitives.bytes32:
        """
        Send tokens
        """
        return primitives.bytes32(
            bytes.fromhex(
                self._exchange_router.send_tokens(
                    (self.collateral_address, ORDER_VAULT_ADDRESS, amount),
                ).data[2:]
            )
        )

    def _send_wnt(self, amount: primitives.uint256) -> primitives.bytes32:
        """
        Send WNT
        """
        return primitives.bytes32(bytes.fromhex(self._exchange_router.send_wnt((ORDER_VAULT_ADDRESS, amount)).data[2:]))

    async def _get_execution_fee(self) -> primitives.uint256:
        await self.determine_gas_limits()
        block = await Block[Arbitrum].latest()
        gas_price = block.base_fee_per_gas
        assert self._gas_limits is not None
        assert gas_price is not None

        assert self._gas_limits_order_type is not None
        execution_fee = get_execution_fee(self._gas_limits, self._gas_limits_order_type, gas_price)

        return primitives.uint256(int(execution_fee * self.execution_buffer))
