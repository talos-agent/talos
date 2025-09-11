from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OraclePriceData(BaseModel):
    id: str
    min_block_number: Optional[int] = Field(None, alias="minBlockNumber")
    min_block_hash: Optional[str] = Field(None, alias="minBlockHash")
    oracle_decimals: Optional[int] = Field(None, alias="oracleDecimals")
    token_symbol: str = Field(alias="tokenSymbol")
    token_address: str = Field(alias="tokenAddress")
    min_price: Optional[float] = Field(None, alias="minPrice")
    max_price: Optional[float] = Field(None, alias="maxPrice")
    signer: Optional[str] = None
    signature: Optional[str] = None
    signature_without_block_hash: Optional[str] = Field(None, alias="signatureWithoutBlockHash")
    created_at: datetime = Field(alias="createdAt")
    min_block_timestamp: int = Field(alias="minBlockTimestamp")
    oracle_keeper_key: str = Field(alias="oracleKeeperKey")
    max_block_timestamp: int = Field(alias="maxBlockTimestamp")
    max_block_number: Optional[int] = Field(None, alias="maxBlockNumber")
    max_block_hash: Optional[str] = Field(None, alias="maxBlockHash")
    max_price_full: str = Field(alias="maxPriceFull")
    min_price_full: str = Field(alias="minPriceFull")
    oracle_keeper_record_id: Optional[str] = Field(None, alias="oracleKeeperRecordId")
    oracle_keeper_fetch_type: str = Field(alias="oracleKeeperFetchType")
    oracle_type: str = Field(alias="oracleType")
    blob: str
    is_valid: bool = Field(alias="isValid")
    invalid_reason: Optional[str] = Field(None, alias="invalidReason")

    class Config:
        populate_by_name = True
