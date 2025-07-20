from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from ..utils.dexscreener import get_ohlcv_data
from .base import SupervisedTool


class DexscreenerToolArgs(BaseModel):
    token_address: str = Field(
        ..., description="The address of the token to get the price for"
    )


class DexscreenerTool(SupervisedTool):
    name: str = "dexscreener_tool"
    description: str = "Gets the price of a token from dexscreener.com"
    args_schema: type[BaseModel] = DexscreenerToolArgs

    def _run_unsupervised(self, token_address: str, **kwargs: Any) -> dict:
        """Gets the price of a token from dexscreener.com"""
        pair_address = "0xdaae914e4bae2aae4f536006c353117b90fb37e3"
        return get_ohlcv_data(pair_address)
