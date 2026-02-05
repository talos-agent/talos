"""
Core visualization functions for the Temporal Weather Map dashboard.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from pydantic import BaseModel, ConfigDict


class ChronofluxDashboard(BaseModel):
    """
    Simulates the visualization logic for the global Chronoflux weather map.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    node_data: Dict[str, Any]

    def render_text_dashboard(self) -> str:
        """
        Renders a ASCII-based dashboard for CLI viewing.
        """
        output = []
        output.append("=" * 60)
        output.append("   EARTH'S TEMPORAL WEATHER MAP (T.E.N.S.O.R.)")
        output.append("=" * 60)

        for node_id, data in self.node_data.items():
            status = "NORMAL" if data.get("Iχ", 0) < 6 else "ANOMALY"
            indicator = "🔵" if status == "NORMAL" else "🔴"
            output.append(
                f"Node {node_id:10} | Iχ: {data.get('Iχ', 0):.2f} | ω: {data.get('omega', 0):.2e} | {indicator} {status}"
            )

        output.append("-" * 60)
        global_mean = np.mean([d.get("Iχ", 0) for d in self.node_data.values()])
        output.append(f"Global Iχ Mean: {global_mean:.2f}")
        output.append("=" * 60)

        return "\n".join(output)
