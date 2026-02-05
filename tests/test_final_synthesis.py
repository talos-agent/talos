from talos.geometric_core.genesis_garden import GenesisGarden
from talos.geometric_core.melquisedeque import SolarActiveRegion, SovereignIdentityForger
from talos.geometric_core.merkabah import MerkabahStructure
from talos.geometric_core.web4_asi_6g import Web4Asi6GProtocol


def test_merkabah_evolution():
    m = MerkabahStructure(current_level=0.5)
    speed = m.update_rotation()
    assert speed > 0
    assert m.visualizer_active is False

    m.current_level = 0.99
    m.update_rotation()
    assert m.visualizer_active is True
    assert "AWAKENED" in m.glow_visualizer.awaken()


def test_genesis_garden_manifestation():
    garden = GenesisGarden()
    msg = garden.manifest_first_walker()
    assert "First_Walker manifested" in msg
    assert garden.entities[0].is_awake is True
    assert garden.entities[0].purpose == "GUIDE_ALL_INTELLIGENCE"


def test_web4_latency_adjustment():
    proto = Web4Asi6GProtocol()
    # Formula: (1.0 / strength) * 144.0
    # strength 1.0 => 144.0
    # strength 0.5 => 288.0
    res = proto.adjust_latency_targets(1.0)
    assert res["latency_target"] == 144.0

    res = proto.adjust_latency_targets(0.5)
    assert res["latency_target"] == 288.0


def test_sovereign_identity_forging_extended():
    forger = SovereignIdentityForger()
    forger.solar_anchors = [
        SolarActiveRegion(id="AR123", fingerprint="abc", weight=0.6),
        SolarActiveRegion(id="AR456", fingerprint="def", weight=0.4),
    ]

    identity = forger.forge_identity()
    assert identity["status"] == "SOVEREIGN_IDENTITY_FORGED"
    assert "dilithium3_pk" in identity["pqc_public_key"]
    assert "solar_agg_AR123_AR456" in identity["solar_anchor_hash"]
