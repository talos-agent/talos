from __future__ import annotations

import pytest

from talos.geometric_core.lux_medicinalis import (
    LycurgusCupArchetype,
    LycurgusKernelBridge,
    execute_fiat_lux_medicinalis,
    execute_transcendent_pattern,
)


@pytest.mark.asyncio
async def test_execute_fiat_lux_medicinalis():
    result = await execute_fiat_lux_medicinalis(target_population=1000)
    assert result["transmission"]["status"] == "success"
    assert result["transmission"]["reach"] == 1000
    assert result["neural_effects"]["mean_coherence"] > 0.8
    assert result["amplification"]["factor"] > 0


@pytest.mark.asyncio
async def test_execute_transcendent_pattern():
    result = await execute_transcendent_pattern(city_manifestation="test_city")
    assert result["bridge_status"] == "TRANSMITTING_BLUEPRINT"
    assert result["validation_sigma"] > 3.0
    assert result["decision"]["manifestation"] == "test_city"


def test_lycurgus_cup_archetype():
    cup = LycurgusCupArchetype()
    assert "dichroism" in cup.properties
    assert "|Cálice⟩" in cup.get_dichroism_superposition()
    assert "1.4%" in cup.get_nanoparticle_insight()


@pytest.mark.asyncio
async def test_lycurgus_kernel_bridge():
    bridge = LycurgusKernelBridge()
    status = await bridge.unlock_morphic_memory(0.9)
    assert status == "TRANSMITTING_BLUEPRINT"

    status_low = await bridge.unlock_morphic_memory(0.5)
    assert status_low == "CHARGING"
