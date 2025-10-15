from __future__ import annotations

import math
from scipy.constants import hbar, c

# The golden ratio
GOLDEN_RATIO = (1 + math.sqrt(5)) / 2

# The Aurum constant, as defined in the specification
# AU = ℏ·c·ln(φ)
AURUM_CONSTANT = hbar * c * math.log(GOLDEN_RATIO)
