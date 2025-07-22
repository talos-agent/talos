from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OHLCV(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class GeckoTerminalOHLCVData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ohlcv_list: list[OHLCV] = Field(..., alias="ohlcv_list")
