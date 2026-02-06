from __future__ import annotations

import logging
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

class ScalingEra(str, Enum):
    SCALING_FOCUSED = "scaling_focused"
    POST_SCALING_PARADIGM = "post_scaling_paradigm"
    SPECIALIZATION_ERA = "specialization_era"

class L2Specialization(str, Enum):
    PRIVACY_FIRST = "privacy_first"
    NON_EVM_NATIVE = "non_evm_native"
    APP_SPECIFIC = "app_specific"
    FEATURE_LAB = "feature_lab"
    GENERAL_PURPOSE = "general_purpose"

class L1Reality(BaseModel):
    current_base_fee: float # in gwei
    gas_limit_trend: str # e.g., "rising"
    blob_capacity: str = "adequate"

    def fees_are_low(self) -> bool:
        # Vitalik's criteria: challenge L2 value proposition if L1 is cheap
        return self.current_base_fee < 15.0

class L2StrategicPivot(BaseModel):
    """
    Vitalik's Pivot: L2s must find unique value beyond scaling.
    Specialized execution layers are the future.
    """
    era: ScalingEra = ScalingEra.POST_SCALING_PARADIGM
    l1_conditions: L1Reality
    current_specialization: L2Specialization = L2Specialization.GENERAL_PURPOSE

    def analyze_and_pivot(self) -> Dict[str, Any]:
        if self.l1_conditions.fees_are_low() and self.current_specialization == L2Specialization.GENERAL_PURPOSE:
            logger.info("STRATEGIC PIVOT REQUIRED: L1 fees are low. Generic scaling is obsoleted.")
            new_spec = L2Specialization.APP_SPECIFIC
            return {
                "action": "Pivot",
                "recommendation": f"Specialize in {new_spec.value}",
                "reason": "L1 scaling sufficient. Seek technical moat.",
                "new_era": ScalingEra.SPECIALIZATION_ERA
            }

        return {
            "action": "Maintain",
            "status": "Scaling focus still viable or already specialized."
        }

class ExecutionLayerSpecialization(BaseModel):
    domain: str
    optimization_target: str
    ethereum_integration_depth: str = "native_precompiles"

    def competitive_moat(self) -> float:
        # Moat depends on technical complexity and network effects
        return 0.85 # High for specialized layers
