from typing import Annotated

from eth_typing import HexAddress

from eth_rpc import ProtocolBase, ContractFunc
from eth_rpc.types import primitives, Name

from .schemas import (
    DepositAmountOutParams,
    ExecutionPriceParams,
    GetMarketsParams,
    GetMarketParams,
    GetOpenInterestParams,
    GetPnlParams,
    GetMarketTokenPriceParams,
    GetMarketTokenPriceResponse,
    SwapAmountOutParams,
    SwapAmountOutResponse,
    WithdrawalAmountOutParams,
    WithdrawalAmountOutResponse
)
from .types import (
    OrderProps,
    ReaderUtilsPositionInfo,
    ReaderPricingUtilsExecutionPriceResult,
    PositionProps,
    MarketProps,
    DepositProps,
    WithdrawalProps,
    ShiftProps,
    PriceProps,
    MarketUtilsMarketPrices,
    ReaderUtilsMarketInfo
)


class SyntheticsReader(ProtocolBase):
    get_account_orders: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.uint256, primitives.uint256],
            list[OrderProps]
        ],
        Name("getAccountOrders"),
    ]

    get_account_position_info_list: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, list[primitives.bytes32], list[MarketUtilsMarketPrices], primitives.address],
            list[ReaderUtilsPositionInfo]
        ],
        Name("getAccountPositionInfoList"),
    ]

    get_account_positions: Annotated[
        ContractFunc[
            tuple[HexAddress, HexAddress, primitives.uint256, primitives.uint256],
            list[PositionProps]
        ],
        Name("getAccountPositions"),
    ]

    get_adl_state: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, bool, MarketUtilsMarketPrices],
            tuple[primitives.uint256, bool, primitives.int256, primitives.uint256]
        ],
        Name("getAdlState"),
    ]

    get_deposit: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            DepositProps
        ],
        Name("getDeposit"),
    ]

    get_deposit_amount_out: Annotated[
        ContractFunc[
            DepositAmountOutParams,
            primitives.uint256
        ],
        Name("getDepositAmountOut"),
    ]

    get_execution_price: Annotated[
        ContractFunc[
            ExecutionPriceParams,
            ReaderPricingUtilsExecutionPriceResult
        ],
        Name("getExecutionPrice"),
    ]

    get_market: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address],
            MarketProps
        ],
        Name("getMarket"),
    ]

    get_market_by_salt: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            MarketProps
        ],
        Name("getMarketBySalt"),
    ]

    get_market_info: Annotated[
        ContractFunc[
            GetMarketParams,
            ReaderUtilsMarketInfo
        ],
        Name("getMarketInfo"),
    ]

    get_market_info_list: Annotated[
        ContractFunc[
            tuple[primitives.address, list[MarketUtilsMarketPrices], primitives.uint256, primitives.uint256],
            list[ReaderUtilsMarketInfo]
        ],
        Name("getMarketInfoList"),
    ]

    get_market_token_price: Annotated[
        ContractFunc[
            GetMarketTokenPriceParams,
            GetMarketTokenPriceResponse,
        ],
        Name("getMarketTokenPrice"),
    ]

    get_markets: Annotated[
        ContractFunc[
            GetMarketsParams,
            list[MarketProps]
        ],
        Name("getMarkets"),
    ]

    get_net_pnl: Annotated[
        ContractFunc[
            tuple[primitives.address, MarketProps, PriceProps, bool],
            primitives.int256
        ],
        Name("getNetPnl"),
    ]

    get_open_interest_with_pnl: Annotated[
        ContractFunc[
            GetOpenInterestParams,
            primitives.int256
        ],
        Name("getOpenInterestWithPnl"),
    ]

    get_order: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            OrderProps
        ],
        Name("getOrder"),
    ]

    get_pnl: Annotated[
        ContractFunc[
            GetPnlParams,
            primitives.int256
        ],
        Name("getPnl"),
    ]

    get_pnl_to_pool_factor: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, MarketUtilsMarketPrices, bool, bool],
            primitives.int256
        ],
        Name("getPnlToPoolFactor"),
    ]

    get_position: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            PositionProps
        ],
        Name("getPosition"),
    ]

    get_position_info: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.bytes32, MarketUtilsMarketPrices, primitives.uint256, primitives.address, bool],
            ReaderUtilsPositionInfo
        ],
        Name("getPositionInfo"),
    ]

    get_position_pnl_usd: Annotated[
        ContractFunc[
            tuple[primitives.address, MarketProps, MarketUtilsMarketPrices, primitives.bytes32, primitives.uint256],
            tuple[primitives.int256, primitives.int256, primitives.uint256]
        ],
        Name("getPositionPnlUsd"),
    ]

    get_shift: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            ShiftProps
        ],
        Name("getShift"),
    ]

    get_swap_amount_out: Annotated[
        ContractFunc[
            SwapAmountOutParams,
            SwapAmountOutResponse,
        ],
        Name("getSwapAmountOut"),
    ]

    get_swap_price_impact: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.address, primitives.address, primitives.uint256, PriceProps, PriceProps],
            tuple[primitives.int256, primitives.int256, primitives.int256]
        ],
        Name("getSwapPriceImpact"),
    ]

    get_withdrawal: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            WithdrawalProps
        ],
        Name("getWithdrawal"),
    ]

    get_withdrawal_amount_out: Annotated[
        ContractFunc[
            WithdrawalAmountOutParams,
            WithdrawalAmountOutResponse,
        ],
        Name("getWithdrawalAmountOut"),
    ]
