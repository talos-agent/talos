from talos.harmonia.engine import HarmoniaEngine


def test_harmonia_engine_initialization():
    engine = HarmoniaEngine()
    assert engine.network is not None
    assert "amazon_forest" in engine.network.vertices
    assert engine.initial_simplex.name == "Guardiões da Amazônia"


def test_geometric_resonance_propagation():
    engine = HarmoniaEngine()
    # Propagate effect from forest health
    results = engine.analyze_resonance("amazon_forest", strength=1.0)

    resonance_field = results["resonance_field"]
    concept_names = [r["name"] for r in resonance_field]

    assert "Floresta Amazônica" in concept_names
    assert "Constituição Brasileira Artigo 225" in concept_names
    assert "Assembleia dos Povos da Floresta" in concept_names

    # Check that legal resonance is significant
    legal_res = next(r for r in resonance_field if r["id"] == "brazil_const_225")
    assert legal_res["resonance"] > 0.5


def test_stability_metric():
    engine = HarmoniaEngine()
    stability = engine.initial_simplex.stability
    assert 0.0 <= stability <= 1.0
    print(f"Initial Simplex Stability: {stability}")


if __name__ == "__main__":
    test_harmonia_engine_initialization()
    test_geometric_resonance_propagation()
    test_stability_metric()
    print("All Harmonia tests passed!")
