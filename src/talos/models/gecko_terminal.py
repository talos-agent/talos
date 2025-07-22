from typing import List

from pydantic import BaseModel, Field


class OHLCV(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class GeckoTerminalOHLCVData(BaseModel):
    ohlcv_list: List[OHLCV] = Field(..., alias="ohlcv_list")

    class Config:
        orm_mode = True
