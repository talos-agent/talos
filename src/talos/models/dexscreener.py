from pydantic import BaseModel, Field


class DexscreenerData(BaseModel):
    price_usd: float = Field(..., alias="priceUsd")
    price_change_h24: float = Field(..., alias="priceChange", description="Price change in the last 24 hours")
    volume_h24: float = Field(..., alias="volume", description="Volume in the last 24 hours")
