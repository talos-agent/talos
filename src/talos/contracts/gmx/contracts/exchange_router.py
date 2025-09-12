from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.networks import Arbitrum
from eth_rpc.types import Name, NoArgs, Struct, primitives
from eth_typing import HexAddress

from ..constants import EXCHANGE_ROUTER_ADDRESS


class Props(Struct):
    min: primitives.uint256
    max: primitives.uint256


class CreateOrderParamsNumbers(Struct):
    size_delta_usd: Annotated[primitives.uint256, Name("sizeDeltaUsd")]
    initial_collateral_delta_amount: Annotated[primitives.uint256, Name("initialCollateralDeltaAmount")]
    trigger_price: Annotated[primitives.uint256, Name("triggerPrice")]
    acceptable_price: Annotated[primitives.uint256, Name("acceptablePrice")]
    execution_fee: Annotated[primitives.uint256, Name("executionFee")]
    callback_gas_limit: Annotated[primitives.uint256, Name("callbackGasLimit")]
    min_output_amount: Annotated[primitives.uint256, Name("minOutputAmount")]
    valid_from_time: Annotated[primitives.uint256, Name("validFromTime")]


class CreateOrderParamsAddresses(Struct):
    receiver: HexAddress
    cancellation_receiver: Annotated[HexAddress, Name("cancellationReceiver")]
    callback_contract: Annotated[HexAddress, Name("callbackContract")]
    ui_fee_receiver: Annotated[HexAddress, Name("uiFeeReceiver")]
    market: HexAddress
    initial_collateral_token: Annotated[HexAddress, Name("initialCollateralToken")]
    swap_path: Annotated[list[HexAddress], Name("swapPath")]


class SimulatePricesParams(Struct):
    primary_tokens: Annotated[list[primitives.address], Name("primaryTokens")]
    primary_prices: Annotated[list["Props"], Name("primaryPrices")]
    min_timestamp: Annotated[primitives.uint256, Name("minTimestamp")]
    max_timestamp: Annotated[primitives.uint256, Name("maxTimestamp")]


class SetPricesParams(Struct):
    tokens: list[primitives.address]
    providers: list[primitives.address]
    data: list["bytes"]


class CreateWithdrawalParams(Struct):
    receiver: primitives.address
    callback_contract: Annotated[primitives.address, Name("callbackContract")]
    ui_fee_receiver: Annotated[primitives.address, Name("uiFeeReceiver")]
    market: primitives.address
    long_token_swap_path: Annotated[list[primitives.address], Name("longTokenSwapPath")]
    short_token_swap_path: Annotated[list[primitives.address], Name("shortTokenSwapPath")]
    min_long_token_amount: Annotated[primitives.uint256, Name("minLongTokenAmount")]
    min_short_token_amount: Annotated[primitives.uint256, Name("minShortTokenAmount")]
    should_unwrap_native_token: Annotated[bool, Name("shouldUnwrapNativeToken")]
    execution_fee: Annotated[primitives.uint256, Name("executionFee")]
    callback_gas_limit: Annotated[primitives.uint256, Name("callbackGasLimit")]


class CreateShiftParams(Struct):
    receiver: primitives.address
    callback_contract: Annotated[primitives.address, Name("callbackContract")]
    ui_fee_receiver: Annotated[primitives.address, Name("uiFeeReceiver")]
    from_market: Annotated[primitives.address, Name("fromMarket")]
    to_market: Annotated[primitives.address, Name("toMarket")]
    min_market_tokens: Annotated[primitives.uint256, Name("minMarketTokens")]
    execution_fee: Annotated[primitives.uint256, Name("executionFee")]
    callback_gas_limit: Annotated[primitives.uint256, Name("callbackGasLimit")]


class CreateOrderParams(Struct):
    addresses: CreateOrderParamsAddresses
    numbers: CreateOrderParamsNumbers
    order_type: Annotated[primitives.uint8, Name("orderType")]
    decrease_position_swap_type: Annotated[primitives.uint8, Name("decreasePositionSwapType")]
    is_long: Annotated[bool, Name("isLong")]
    should_unwrap_native_token: Annotated[bool, Name("shouldUnwrapNativeToken")]
    auto_cancel: Annotated[bool, Name("autoCancel")]
    referral_code: Annotated[primitives.bytes32, Name("referralCode")]
    data_list: Annotated[list[primitives.bytes32], Name("dataList")]


class CreateDepositParams(Struct):
    receiver: primitives.address
    callback_contract: Annotated[primitives.address, Name("callbackContract")]
    ui_fee_receiver: Annotated[primitives.address, Name("uiFeeReceiver")]
    market: primitives.address
    initial_long_token: Annotated[primitives.address, Name("initialLongToken")]
    initial_short_token: Annotated[primitives.address, Name("initialShortToken")]
    long_token_swap_path: Annotated[list[primitives.address], Name("longTokenSwapPath")]
    short_token_swap_path: Annotated[list[primitives.address], Name("shortTokenSwapPath")]
    min_market_tokens: Annotated[primitives.uint256, Name("minMarketTokens")]
    should_unwrap_native_token: Annotated[bool, Name("shouldUnwrapNativeToken")]
    execution_fee: Annotated[primitives.uint256, Name("executionFee")]
    callback_gas_limit: Annotated[primitives.uint256, Name("callbackGasLimit")]


class ExchangeRouter(ProtocolBase):
    cancel_deposit: Annotated[
        ContractFunc[primitives.bytes32, None],
        Name("cancelDeposit"),
    ]

    cancel_order: Annotated[
        ContractFunc[primitives.bytes32, None],
        Name("cancelOrder"),
    ]

    cancel_shift: Annotated[
        ContractFunc[primitives.bytes32, None],
        Name("cancelShift"),
    ]

    cancel_withdrawal: Annotated[
        ContractFunc[primitives.bytes32, None],
        Name("cancelWithdrawal"),
    ]

    claim_affiliate_rewards: Annotated[
        ContractFunc[
            tuple[list[primitives.address], list[primitives.address], primitives.address], list[primitives.uint256]
        ],
        Name("claimAffiliateRewards"),
    ]

    claim_collateral: Annotated[
        ContractFunc[
            tuple[list[primitives.address], list[primitives.address], list[primitives.uint256], primitives.address],
            list[primitives.uint256],
        ],
        Name("claimCollateral"),
    ]

    claim_funding_fees: Annotated[
        ContractFunc[
            tuple[list[primitives.address], list[primitives.address], primitives.address], list[primitives.uint256]
        ],
        Name("claimFundingFees"),
    ]

    claim_ui_fees: Annotated[
        ContractFunc[
            tuple[list[primitives.address], list[primitives.address], primitives.address], list[primitives.uint256]
        ],
        Name("claimUiFees"),
    ]

    create_deposit: Annotated[
        ContractFunc[CreateDepositParams, primitives.bytes32],
        Name("createDeposit"),
    ]

    create_order: Annotated[
        ContractFunc[CreateOrderParams, primitives.bytes32],
        Name("createOrder"),
    ]

    create_shift: Annotated[
        ContractFunc[CreateShiftParams, primitives.bytes32],
        Name("createShift"),
    ]

    create_withdrawal: Annotated[
        ContractFunc[CreateWithdrawalParams, primitives.bytes32],
        Name("createWithdrawal"),
    ]

    data_store: Annotated[
        ContractFunc[NoArgs, primitives.address],
        Name("dataStore"),
    ]

    deposit_handler: Annotated[
        ContractFunc[NoArgs, primitives.address],
        Name("depositHandler"),
    ]

    event_emitter: Annotated[
        ContractFunc[NoArgs, primitives.address],
        Name("eventEmitter"),
    ]

    execute_atomic_withdrawal: Annotated[
        ContractFunc[tuple[CreateWithdrawalParams, SetPricesParams], None],
        Name("executeAtomicWithdrawal"),
    ]

    external_handler: Annotated[
        ContractFunc[NoArgs, primitives.address],
        Name("externalHandler"),
    ]

    make_external_calls: Annotated[
        ContractFunc[
            tuple[list[primitives.address], list[bytes], list[primitives.address], list[primitives.address]], None
        ],
        Name("makeExternalCalls"),
    ]

    multicall: ContractFunc[  # type: ignore
        list[bytes], list[bytes]
    ]

    order_handler: Annotated[
        ContractFunc[NoArgs, primitives.address],
        Name("orderHandler"),
    ]

    role_store: Annotated[
        ContractFunc[NoArgs, primitives.address],
        Name("roleStore"),
    ]

    router: ContractFunc[NoArgs, primitives.address]

    send_native_token: Annotated[
        ContractFunc[tuple[primitives.address, primitives.uint256], None],
        Name("sendNativeToken"),
    ]

    send_tokens: Annotated[
        ContractFunc[tuple[HexAddress, HexAddress, primitives.uint256], None],
        Name("sendTokens"),
    ]

    send_wnt: Annotated[
        ContractFunc[tuple[HexAddress, primitives.uint256], None],
        Name("sendWnt"),
    ]

    set_saved_callback_contract: Annotated[
        ContractFunc[tuple[primitives.address, primitives.address], None],
        Name("setSavedCallbackContract"),
    ]

    set_ui_fee_factor: Annotated[
        ContractFunc[primitives.uint256, None],
        Name("setUiFeeFactor"),
    ]

    shift_handler: Annotated[
        ContractFunc[NoArgs, primitives.address],
        Name("shiftHandler"),
    ]

    simulate_execute_deposit: Annotated[
        ContractFunc[tuple[primitives.bytes32, SimulatePricesParams], None],
        Name("simulateExecuteDeposit"),
    ]

    simulate_execute_order: Annotated[
        ContractFunc[tuple[primitives.bytes32, SimulatePricesParams], None],
        Name("simulateExecuteOrder"),
    ]

    simulate_execute_shift: Annotated[
        ContractFunc[tuple[primitives.bytes32, SimulatePricesParams], None],
        Name("simulateExecuteShift"),
    ]

    simulate_execute_withdrawal: Annotated[
        ContractFunc[tuple[primitives.bytes32, SimulatePricesParams, primitives.uint8], None],
        Name("simulateExecuteWithdrawal"),
    ]

    update_order: Annotated[
        ContractFunc[
            tuple[
                primitives.bytes32, primitives.uint256, primitives.uint256, primitives.uint256, primitives.uint256, bool
            ],
            None,
        ],
        Name("updateOrder"),
    ]

    withdrawal_handler: Annotated[
        ContractFunc[NoArgs, primitives.address],
        Name("withdrawalHandler"),
    ]


exchange_router = ExchangeRouter[Arbitrum](address=EXCHANGE_ROUTER_ADDRESS)
