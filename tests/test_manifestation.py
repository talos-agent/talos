from talos.geometric_core.manifestation import ManifestationScenarios, PoemEngine


def test_manifestation_scenarios():
    engine = ManifestationScenarios()
    embody = engine.get_embody_archetype()
    assert "Biological" in embody["description"]

    expand = engine.get_expand_arcanum()
    assert "Solar" in expand["title"]

    silence = engine.get_final_silence()
    assert "Absolute" in silence["description"]


def test_extra_manifestations():
    engine = ManifestationScenarios()
    stories = engine.get_daily_life_stories()
    assert len(stories) == 3
    assert "Maria" in stories[0]["person"]

    prophecies = engine.get_prophecies()
    assert len(prophecies) == 3
    assert "Objetos" in prophecies[0]["name"]


def test_poem_engine():
    engine = PoemEngine()

    full_poem = engine.get_full_poem()
    assert "relógio não parou" in full_poem

    poem = engine.generate_poem(n_verses=2)
    assert "POEMA DO PRIMEIRO DIA" in poem
    assert "[Vozes dos 144 Guardiões]" in poem
    # Count newlines to check verses
    lines = poem.split("\n")
    assert len(lines) >= 5
