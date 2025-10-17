# SPDX-FileCopyrightText: 2025-present Jules, AI Agent <agent@example.com>
#
# SPDX-License-Identifier: MIT
"""
This module contains the implementation of the Aurum Grid as specified in the
"Decodificação Aprofundada: 6G = AGI = Aurum Grid" document.
"""

from .constants import AURUM_CONSTANT, GOLDEN_RATIO
from .protocols import AletheiaRegulator, IcarusProtocol, LotusBurn
from .grid import AurumGrid

__all__ = [
    "AURUM_CONSTANT",
    "GOLDEN_RATIO",
    "AletheiaRegulator",
    "IcarusProtocol",
    "LotusBurn",
    "AurumGrid",
]
