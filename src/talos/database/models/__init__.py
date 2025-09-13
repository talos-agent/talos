from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from .chainlink import ChainlinkBridge


class Counter(Base):
    __tablename__ = "counters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    value: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Swap(Base):
    __tablename__ = "swaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    strategy_id: Mapped[str] = mapped_column(String(255), nullable=False)
    transaction_hash: Mapped[str] = mapped_column(String(66), nullable=False)
    chain_id: Mapped[int] = mapped_column(Integer, nullable=False)
    wallet_address: Mapped[str] = mapped_column(String(42), nullable=False)
    amount_in: Mapped[int] = mapped_column(Numeric(78), nullable=False)
    token_in: Mapped[str] = mapped_column(String(42), nullable=False)
    amount_out: Mapped[int] = mapped_column(
        Numeric(78), nullable=False
    )  # uint256 max is 2^256-1, needs 78 decimal digits
    token_out: Mapped[str] = mapped_column(String(42), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_temporary: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_active: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    conversations: Mapped[List["ConversationHistory"]] = relationship(
        "ConversationHistory", back_populates="user", cascade="all, delete-orphan"
    )
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="user", cascade="all, delete-orphan")


class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("conversation_history.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'human', 'ai', 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="messages")
    conversation: Mapped["ConversationHistory"] = relationship("ConversationHistory", back_populates="messages")


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    memory_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship("User")


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    dataset_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User")
    chunks: Mapped[List["DatasetChunk"]] = relationship(
        "DatasetChunk", back_populates="dataset", cascade="all, delete-orphan"
    )


class DatasetChunk(Base):
    __tablename__ = "dataset_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("datasets.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="chunks")


class ContractDeployment(Base):
    __tablename__ = "contract_deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    contract_signature: Mapped[str] = mapped_column(String(66), nullable=False, index=True)
    contract_address: Mapped[str] = mapped_column(String(42), nullable=False, index=True)
    chain_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    salt: Mapped[str] = mapped_column(String(66), nullable=False)
    bytecode_hash: Mapped[str] = mapped_column(String(66), nullable=False)
    deployment_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    transaction_hash: Mapped[str] = mapped_column(String(66), nullable=False)
    deployed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship("User")

    __table_args__ = (Index("idx_signature_chain", "contract_signature", "chain_id", unique=True),)


__all__ = [
    "Base",
    "Counter",
    "Swap",
    "User",
    "ConversationHistory",
    "Message",
    "Memory",
    "Dataset",
    "DatasetChunk",
    "ContractDeployment",
    "ChainlinkBridge",
]
