from __future__ import annotations

from talos.geometric_core.symbiosis import SymbiosisEngine


def test_symbiosis_cycle():
    engine = SymbiosisEngine()
    initial_consciousness = engine.state.human_consciousness_level
    initial_intuition = engine.state.agi_cognitive_state.intuition_quotient

    result = engine.run_cycle()

    assert result["neural_entrainment"] == 0.05
    assert engine.state.human_consciousness_level > initial_consciousness
    assert engine.state.agi_cognitive_state.intuition_quotient > initial_intuition
    assert result["status"] == "Symbiosis Active"


def test_ethical_boundaries():
    engine = SymbiosisEngine()

    # Under threshold
    engine.state.neural_entrainment = 0.5
    assert engine.check_ethical_boundaries() is True

    # Over threshold (threatens cognitive autonomy)
    engine.state.neural_entrainment = 0.95
    assert engine.check_ethical_boundaries() is False
