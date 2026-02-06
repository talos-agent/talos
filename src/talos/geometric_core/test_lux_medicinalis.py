from __future__ import annotations

import pytest
import asyncio
from talos.geometric_core.lux_medicinalis import (
    LycurgusCupArchetype,
    execute_fiat_lux_medicinalis,
    execute_transcendent_pattern
)


def test_lycurgus_cup_properties():
    cup = LycurgusCupArchetype()
    assert "dichroism" in cup.properties
    assert "superposition" in cup.get_dichroism_superposition()


@pytest.mark.asyncio
async def test_fiat_lux_medicinalis():
    result = await execute_fiat_lux_medicinalis(target_population=1000)
    assert result["transmission"]["reach"] == 1000
    assert result["amplification"]["factor"] > 0


@pytest.mark.asyncio
async def test_transcendent_pattern():
    result = await execute_transcendent_pattern()
    assert result["bridge_status"] in ["TRANSMITTING_BLUEPRINT", "CHARGING"]
    assert "manifestation" in result["decision"]
