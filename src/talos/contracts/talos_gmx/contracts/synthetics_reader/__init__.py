from eth_rpc.networks import Arbitrum

from .reader import SyntheticsReader
from .schemas import (
    DepositAmountOutParams,
    ExecutionPriceParams,
    GetMarketParams,
    GetMarketsParams,
    GetOpenInterestParams,
    GetPnlParams,
)
from .types import (
    MarketProps,
    MarketUtilsMarketPrices,
    OrderProps,
    PositionProps,
    PriceProps,
    ReaderPricingUtilsExecutionPriceResult,
    ReaderUtilsMarketInfo,
    ReaderUtilsPositionInfo,
)

synthetics_reader = SyntheticsReader[Arbitrum](address="0x5Ca84c34a381434786738735265b9f3FD814b824")


__all__ = [
    "DepositAmountOutParams",
    "ExecutionPriceParams",
    "GetMarketsParams",
    "GetOpenInterestParams",
    "GetPnlParams",
    "MarketProps",
    "ReaderUtilsMarketInfo",
    "SyntheticsReader",
    "PositionProps",
    "OrderProps",
    "PriceProps",
    "ReaderUtilsPositionInfo",
    "ReaderPricingUtilsExecutionPriceResult",
    "reader_contract",
    "SyntheticsReader",
    "GetMarketParams",
    "MarketUtilsMarketPrices",
    "PositionProps",
    "OrderProps",
    "PriceProps",
    "ReaderUtilsPositionInfo",
    "ReaderPricingUtilsExecutionPriceResult",
    "reader_contract",
]
