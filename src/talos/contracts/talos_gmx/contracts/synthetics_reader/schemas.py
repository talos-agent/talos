from typing import Annotated

from eth_typing import HexAddress
from pydantic import BaseModel

from eth_rpc.types import primitives, Name
from .enums import SwapPricingType
from .types import MarketProps, MarketUtilsMarketPrices, MarketPoolValueInfoProps, PriceProps, SwapPricingUtilsSwapFees


class ExecutionPriceParams(BaseModel):
    data_store: Annotated[primitives.address, Name("dataStore")]
    market_key: Annotated[primitives.address, Name("marketKey")]
    index_token_price: Annotated[PriceProps, Name("indexTokenPrice")]
    position_size_in_usd: Annotated[primitives.uint256, Name("positionSizeInUsd")]
    position_size_in_tokens: Annotated[primitives.uint256, Name("positionSizeInTokens")]
    size_delta_usd: Annotated[primitives.int256, Name("sizeDeltaUsd")]
    is_long: Annotated[bool, Name("isLong")]


class SwapAmountOutParams(BaseModel):
    data_store: Annotated[primitives.address, Name("dataStore")]
    market: MarketProps
    prices: MarketUtilsMarketPrices
    token_in: primitives.address
    amount_in: primitives.address
    ui_fee_receiver: primitives.address


class SwapAmountOutResponse(BaseModel):
    cache_amount_out: primitives.uint256
    impactAmount: primitives.uint256
    fees: SwapPricingUtilsSwapFees


class DepositAmountOutParams(BaseModel):
    data_store: primitives.address
    market: MarketProps
    prices: MarketUtilsMarketPrices
    long_token_amount: primitives.uint256
    short_token_amount: primitives.uint256
    ui_fee_receiver: primitives.address
    swap_pricing_type: SwapPricingType
    include_virtual_inventory_impact: bool


class WithdrawalAmountOutParams(BaseModel):
    data_store: primitives.address
    market: MarketProps
    prices: MarketUtilsMarketPrices
    market_token_amount: primitives.uint256
    ui_fee_receiver: primitives.address
    swap_pricing_type: SwapPricingType


class WithdrawalAmountOutResponse(BaseModel):
    long_amount_after_fees: primitives.uint256
    short_amount_after_fees: primitives.uint256


class GetMarketsParams(BaseModel):
    data_store: HexAddress
    start_index: primitives.uint256
    end_index: primitives.uint256


class GetOpenInterestParams(BaseModel):
    data_store: HexAddress
    market: MarketProps
    index_token_price: PriceProps
    is_long: bool
    maximize: bool


class GetPnlParams(BaseModel):
    data_store: HexAddress
    market: MarketProps
    index_token_price: PriceProps
    is_long: bool
    maximize: bool


class GetMarketParams(BaseModel):
    data_store: HexAddress
    prices: MarketUtilsMarketPrices
    market_key: HexAddress


class GetMarketTokenPriceParams(BaseModel):
    data_store: primitives.address
    market: MarketProps
    index_token_price: PriceProps
    long_token_price: PriceProps
    short_token_price: PriceProps
    pnl_factor_type: primitives.bytes32
    maximize: bool


class GetMarketTokenPriceResponse(BaseModel):
    market_token_price: primitives.int256
    pool_value_info: MarketPoolValueInfoProps
