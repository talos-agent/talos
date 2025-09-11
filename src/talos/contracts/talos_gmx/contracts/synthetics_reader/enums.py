from enum import IntEnum


class SwapPricingType(IntEnum):
    Swap = 0
    Shift = 1
    Atomic = 2
    Deposit = 3
    Withdrawal = 4


class OrderType(IntEnum):
    MarketSwap = 0
    LimitSwap = 1
    MarketIncrease = 2
    LimitIncrease = 3
    MarketDecrease = 4
    LimitDecrease = 5
    StopLossDecrease = 6
    Liquidation = 7


class DecreasePositionSwapType(IntEnum):
    NoSwap = 0
    SwapPnlTokenToCollateralToken = 1
    SwapCollateralTokenToPnlToken = 2
