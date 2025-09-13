from datetime import datetime
from typing import Any, Optional

from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class TransactionHashItem(BaseModel):
    message_id: HexStr

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class CCIPMessageStatusResponse(BaseModel):
    dest_transaction_hash: list[Any]
    transaction_hash: list[TransactionHashItem]
    message_id: list[Any]

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class TokenAmount(BaseModel):
    token: HexAddress
    amount: str

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class CCIPMessageResponse(BaseModel):
    message_id: HexStr
    state: Optional[Any] = None
    votes: Optional[Any] = None
    source_network_name: str
    dest_network_name: str
    commit_block_timestamp: Optional[Any] = None
    root: Optional[Any] = None
    send_finalized: Optional[Any] = None
    commit_store: HexAddress
    origin: HexAddress
    sequence_number: int
    sender: HexAddress
    receiver: HexAddress
    router_address: HexAddress
    onramp_address: HexAddress
    offramp_address: HexAddress
    dest_router_address: HexAddress
    send_transaction_hash: HexStr
    send_timestamp: datetime
    send_block: int
    send_log_index: int
    min: Optional[Any] = None
    max: Optional[Any] = None
    commit_transaction_hash: Optional[HexStr] = None
    commit_block_number: Optional[int] = None
    commit_log_index: Optional[int] = None
    arm: HexAddress
    bless_transaction_hash: Optional[HexStr] = None
    bless_block_number: Optional[int] = None
    bless_block_timestamp: Optional[datetime] = None
    bless_log_index: Optional[int] = None
    receipt_transaction_hash: Optional[HexStr] = None
    receipt_timestamp: Optional[datetime] = None
    receipt_block: Optional[int] = None
    receipt_log_index: Optional[int] = None
    receipt_finalized: Optional[Any] = None
    data: HexStr
    strict: bool
    nonce: int
    fee_token: HexAddress
    gas_limit: str
    fee_token_amount: str
    token_amounts: list[TokenAmount]
    info_raw: str
    fast_filled: bool
    permission_less_execution_threshold_seconds: int

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
