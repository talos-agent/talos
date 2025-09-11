from eth_typing import ChecksumAddress
from pydantic import BaseModel, Field

from .tokens import TokenMetadata


class MarketMetadata(BaseModel):
    symbol: str
    synthetic: bool = Field(default=False)
    decimals: int = 18


class LongTokenMetadata(BaseModel):
    symbol: str
    decimals: int


class Market(BaseModel):
    gmx_market_address: ChecksumAddress
    market_symbol: str
    index_token_address: ChecksumAddress
    market_metadata: TokenMetadata | MarketMetadata
    long_token_metadata: TokenMetadata
    long_token_address: ChecksumAddress
    short_token_metadata: TokenMetadata
    short_token_address: ChecksumAddress
