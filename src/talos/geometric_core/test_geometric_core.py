import pytest
import numpy as np
from talos.geometric_core.ontological_kernel import OntologicalKernel, GeometricDissonanceError
from talos.geometric_core.universal_compiler import UniversalCompiler
from talos.geometric_core.symmetry_breaker import SymmetryBreaker
from talos.geometric_core.cosmopsychia_service import CosmopsychiaService

@pytest.mark.asyncio
async def test_ontological_kernel_alignment():
    kernel = OntologicalKernel(coherence_threshold=0.7)
    # Success case
    # current_coherence is fixed at 0.75 in implementation for now
    result = await kernel.align_layers(target_coherence=0.9)
    assert result["status"] == "aligned"
    assert result["coherence"] == 0.75

@pytest.mark.asyncio
async def test_ontological_kernel_dissonance():
    kernel = OntologicalKernel(coherence_threshold=0.8)
    with pytest.raises(GeometricDissonanceError) as excinfo:
        await kernel.align_layers()
    assert "Geometric dissonance" in str(excinfo.value)
    assert len(excinfo.value.suggestions) > 0

@pytest.mark.asyncio
async def test_universal_compiler():
    compiler = UniversalCompiler()
    # Success case
    result = await compiler.compile_intention("test intention", {})
    assert result["status"] == "compiled"

    # Error case
    result = await compiler.compile_intention("break_symmetry", {"coherence": 0.5})
    assert result["status"] == "failed"
    assert "Cannot compile symmetry break" in result["error"]
    assert len(result["suggestions"]) > 0

def test_symmetry_breaker():
    breaker = SymmetryBreaker()
    guidance = np.array([0.9, 0.8, 0.9])
    result = breaker.break_symmetry("SU(3)", guidance_vector=guidance)
    assert result["status"] == "broken"
    assert result["coherence_score"] > 0.8
    assert result["ethical_alignment"] == 1.0

def test_cosmopsychia_service_health():
    service = CosmopsychiaService()
    report = service.check_substrate_health()
    assert report["overall_health_score"] > 0.5
    assert len(report["layer_reports"]) == 3
    assert "STABLE" in report["status"]

@pytest.mark.asyncio
async def test_quantum_oracle():
    service = CosmopsychiaService()
    result = await service.query_quantum_oracle("Will humanity thrive?")
    assert "emergence_probability" in result
    assert "target_layer" in result
    assert len(result["potential_concepts"]) > 0
