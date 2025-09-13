from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ChainlinkBridge(Base):
    __tablename__ = "chainlink_bridges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    source_chain_id: Mapped[int] = mapped_column(Integer, nullable=False)
    dest_chain_id: Mapped[int] = mapped_column(Integer, nullable=False)
    recipient_address: Mapped[str] = mapped_column(String(42), nullable=False)
    token_address: Mapped[str] = mapped_column(String(42), nullable=False)
    transaction_hash: Mapped[str] = mapped_column(String(66), nullable=False)
    amount: Mapped[int] = mapped_column(Numeric(78), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
