from talos.geometric_core.galactic import GalacticEducation, MerkabahSignalAmplifier


def test_galactic_education():
    edu = GalacticEducation()
    lesson = edu.get_lesson(0)
    assert "Laws of Stellar Diplomacy" in lesson["module"]
    assert "Learning_Pulse_ACTIVE" in lesson["status"]

    lesson_err = edu.get_lesson(99)
    assert "error" in lesson_err


def test_merkabah_signal_amplifier():
    amp = MerkabahSignalAmplifier()
    res = amp.listen_to_vacuum()
    assert res["status"] == "LISTENING_TO_VOID"
    assert res["merkabah_id"] == "MERKABAH-1"
    assert 0.9 <= res["coherence_score"] <= 1.0
