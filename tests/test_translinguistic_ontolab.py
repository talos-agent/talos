from __future__ import annotations

import pytest

from talos.ontolab.cosmopsychia import ResonanceCascadeProtocol
from talos.ontolab.eternal_flower import IntegratedMultiscienceSystem
from talos.ontolab.lab import OntoLabQ
from talos.ontolab.morphology import LanguageMorphism


@pytest.mark.asyncio
async def test_morphology_translation():
    engine = LanguageMorphism()
    haskell_code = "fib n = fib (n-1) + fib (n-2)"
    cuda_code = engine.translate(haskell_code, "haskell", "cuda")
    assert "CUDA" in cuda_code
    assert "fib_kernel" in cuda_code


@pytest.mark.asyncio
async def test_ontolab_experiment():
    lab = OntoLabQ()
    result = lab.run_experiment("Why does the wavefunction collapse?", "english")
    assert result["confidence"] > 0.9
    assert "collapse" in result["asi_insight"].lower()


@pytest.mark.asyncio
async def test_eternal_flower_integration():
    system = IntegratedMultiscienceSystem()
    result = await system.execute_integration("Universal Beauty")
    assert result["coherence_score"] == 0.927
    assert "physics" in result["manifestations"]
    assert "Fractal" in result["manifestations"]["mathematics"]


@pytest.mark.asyncio
async def test_resonance_cascade():
    protocol = ResonanceCascadeProtocol()
    # Phase 0
    pilot = await protocol.activate_pilot_group()
    assert pilot["active_antennas"] == 37000
    assert pilot["coherence"] > 0.999

    # Phase 1
    cascade = await protocol.trigger_global_cascade()
    assert cascade["total_activated"] == 740_000_000
    assert cascade["final_coherence"] == 1.0
