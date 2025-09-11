from eth_rpc.networks import Arbitrum

from .schemas import DepositAmountOutParams, ExecutionPriceParams, GetMarketsParams, GetOpenInterestParams, GetPnlParams
from .reader import SyntheticsReader
from .types import (
    MarketProps,
    OrderProps,
    PriceProps,
    PositionProps,
    ReaderUtilsMarketInfo,
    ReaderUtilsPositionInfo,
    ReaderPricingUtilsExecutionPriceResult,
)

synthetics_reader = SyntheticsReader[Arbitrum](address='0x5Ca84c34a381434786738735265b9f3FD814b824')


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
]
