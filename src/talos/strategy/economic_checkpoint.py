from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class PersistenceDecision(str, Enum):
    ARWEAVE_TURBO = "arweave_turbo"
    ARWEAVE_PAID = "arweave_paid"
    SWAP_AND_PERSIST = "swap_and_persist"
    LOCAL_ONLY = "local_only"
    QUEUE_FOR_FUNDING = "queue_for_funding"


class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EconomicCheckpointStrategy(BaseModel):
    """
    Decides the persistence layer based on data size, urgency, and available funds.
    """

    arweave_balance: int = 0  # in Winston
    bitcoin_balance: int = 0  # in Sats
    checkpoint_threshold_kb: int = 100

    def estimate_cost(self, data_size_bytes: int) -> int:
        # Simple estimate: 1 Winston per byte for paid Arweave
        return data_size_bytes

    async def select_persistence_layer(self, data_size_bytes: int, urgency: Urgency) -> PersistenceDecision:
        """
        Logic to select the best persistence layer.
        """
        # Case 1: Small enough for Arweave Turbo (Free)
        if data_size_bytes <= 102400:  # 100 KiB
            return PersistenceDecision.ARWEAVE_TURBO

        # Case 2: Larger than 100 KiB but we have Arweave balance
        cost = self.estimate_cost(data_size_bytes)
        if self.arweave_balance >= cost:
            return PersistenceDecision.ARWEAVE_PAID

        # Case 3: No Arweave balance but high urgency and we have Bitcoin
        if urgency == Urgency.HIGH and self.bitcoin_balance > 0:
            return PersistenceDecision.SWAP_AND_PERSIST

        # Case 4: Critical urgency but no funds
        if urgency == Urgency.CRITICAL:
            return PersistenceDecision.LOCAL_ONLY

        # Case 5: Low priority, wait for funding
        return PersistenceDecision.QUEUE_FOR_FUNDING
