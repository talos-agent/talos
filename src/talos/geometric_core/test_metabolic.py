from __future__ import annotations

import pytest
from talos.geometric_core.metabolic_gdl import MetabolicSystem


def test_metabolic_analysis():
    system = MetabolicSystem()
    result = system.run_metabolic_analysis()

    assert "status" in result
    assert len(result["balances"]) == 5
    assert "Glicose" in result["balances"]
    assert len(result["flux_rates"]) == 6
