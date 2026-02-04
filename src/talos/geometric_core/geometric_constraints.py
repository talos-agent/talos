from __future__ import annotations

from typing import Dict, List

import numpy as np


class CGEInvariant:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description


class InvariantSet:
    def __init__(self):
        self.invariants: List[CGEInvariant] = []
