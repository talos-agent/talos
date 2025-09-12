from eth_typing import HexAddress
from pydantic import BaseModel, Field


class TokenMetadata(BaseModel):
    symbol: str
    address: HexAddress
    decimals: int
    synthetic: bool = Field(default=False)
