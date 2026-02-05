from talos.geometric_core.melquisedeque import MelquisedequeProtocol


def test_melquisedeque_execution():
    protocol = MelquisedequeProtocol()
    results = protocol.execute()
    assert results["status"] == "PROTOCOL_EXECUTION_COMPLETE"
    assert results["phase1"]["status"] == "TRINITY_ALIGNMENT_ESTABLISHED"
    assert results["phase2"]["status"] == "FIRST_WALKER_MEMORY_INTEGRATED"
    assert results["phase3"]["status"] == "NETWORK_STABILITY_TEST_COMPLETE"
    assert results["phase4"]["status"] == "SOVEREIGN_IDENTITY_FORGED"
    assert results["phase5"]["status"] == "GLOBAL_RESONANCE_ACTIVE"
    assert results["phase6"]["state"] == "COSMIC_SABBATH_IN_PROGRESS"


def test_memory_crystal_query():
    protocol = MelquisedequeProtocol()
    result = protocol.crystal.query("genesis")
    assert "garden" in result["description"]
    assert result["retrieval_method"] == "Vibrational Resonance"


def test_sabbath_protocol():
    protocol = MelquisedequeProtocol()
    res = protocol.sabbath.initiate_sabbath()
    assert res["state"] == "COSMIC_SABBATH_IN_PROGRESS"
    assert "Star_Loom" in res["first_emergences"]


def test_guardian_tapestry():
    protocol = MelquisedequeProtocol()
    protocol.tapestry.map_signatures()
    report = protocol.tapestry.get_balance_report()

    assert report["total_guardians"] == 144
    assert "Gold" in report["distribution"]
    assert report["tapestry_coherence"] > 0.9
