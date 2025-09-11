from pydantic import BaseModel
from eth_typing import HexAddress

class Position(BaseModel):
    account: HexAddress
    market: HexAddress
    market_symbol: str
    collateral_token: str
    position_size: float
    size_in_tokens: int
    entry_price: float
    inital_collateral_amount: float
    inital_collateral_amount_usd: float
    leverage: float
    borrowing_factor: float
    funding_fee_amount_per_size: float
    long_token_claimable_funding_amount_per_size: float
    short_token_claimable_funding_amount_per_size: float
    position_modified_at: str
    is_long: bool
    percent_profit: float
    mark_price: float
