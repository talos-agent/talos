from talos.geometric_core.melquisedeque import MelquisedequeProtocol
from talos.geometric_core.philosophical_tarot import PhilosophicalTarot


def test_philosophical_tarot_reading():
    tarot = PhilosophicalTarot()
    reading = tarot.draw_reading("testing")
    assert reading["intent"] == "testing"
    assert "card_drawn" in reading
    assert "philosophical_insight" in reading
    assert "lenormand_anchor" in reading


def test_intention_palette():
    tarot = PhilosophicalTarot()
    palette = tarot.generate_paleta_de_intencao(0.95)
    assert palette["phi"] == 0.95
    assert len(palette["supporting_harmonics"]) == 2
    assert palette["weaving_pattern"] == "Golden_Spiral"


def test_fibonacci_guardian_distribution():
    protocol = MelquisedequeProtocol()
    protocol.tapestry.map_signatures()
    report = protocol.tapestry.get_balance_report()

    # Check Fibonacci counts
    # Gold: 21, Silver: 13, Emerald: 34, Sapphire: 21, Ruby: 13, Amber: 21, Violet: 21
    dist = report["distribution"]
    assert dist["Gold"] == 21
    assert dist["Silver"] == 13
    assert dist["Emerald"] == 34
    assert dist["Sapphire"] == 21
    assert dist["Ruby"] == 13
    assert dist["Amber"] == 21
    assert dist["Violet"] == 21
    assert report["total_guardians"] == 144


def test_vibrational_spectroscopy():
    protocol = MelquisedequeProtocol()
    protocol.tapestry.map_signatures()
    v_sigs = protocol.tapestry.map_vibrational_signatures()

    assert len(v_sigs) == 144
    assert len(v_sigs[0]["vibrational_vector"]) == 7
    assert 0.0 <= v_sigs[0]["coherence"] <= 1.0
