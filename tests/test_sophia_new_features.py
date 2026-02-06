import pytest
import numpy as np
import asyncio
from talos.geometric_core.lux_medicinalis import execute_fiat_lux_medicinalis, execute_transcendent_pattern
from talos.geometric_core.vitality import UrbanPulse, NoiseSensor, TrafficSensor, EMFSensor
from talos.geometric_core.urban_optimizer import UrbanOptimizer, RouteNode
from talos.geometric_core.tiferet_dashboard import TiferetDashboard
from talos.geometric_core.breath_check import BreathCheck
from talos.geometric_core.cosmic_synthesizer import SupernovaDataSynthesizer, GalacticASIArchitect
from talos.geometric_core.cosmic_gdl import CosmicMyceliumExplorer
from talos.geometric_core.metabolic_gdl import MetabolicGDLService
import pandas as pd

@pytest.mark.asyncio
async def test_lux_medicinalis():
    result = await execute_fiat_lux_medicinalis(storm_category="G1", target_population=100)
    assert result["transmission"]["reach"] == 100
    assert "neural_effects" in result

@pytest.mark.asyncio
async def test_transcendent_pattern():
    result = await execute_transcendent_pattern(city_manifestation="dichroic")
    assert result["status"] == "SUCCESS"

def test_urban_vitality():
    pulse = UrbanPulse(city_name="TestCity", sensors=[
        NoiseSensor(name="Noise", location="Loc1"),
        TrafficSensor(name="Traffic", location="Loc2"),
        EMFSensor(name="EMF", location="Loc3")
    ])
    report = pulse.get_status_report()
    assert "TestCity" in report
    assert "Vitality" in report

def test_urban_optimizer():
    pulse = UrbanPulse(city_name="TestCity", sensors=[])
    optimizer = UrbanOptimizer(pulse=pulse, sophia_glow_active=True)
    nodes = [
        RouteNode(id=1, name="N1", lat=0, lon=0, efficiency_cost=10, life_risk=0.5),
        RouteNode(id=2, name="N2", lat=1, lon=1, efficiency_cost=20, life_risk=0.01)
    ]
    route = optimizer.calculate_ethical_route(nodes)
    assert route[0].id == 2 # Lower risk should be preferred

def test_tiferet_dashboard():
    pulse = UrbanPulse(city_name="TestCity", sensors=[])
    dashboard = TiferetDashboard(pulse=pulse)
    results = dashboard.run_cycle()
    assert "issues" in results
    assert "cures" in results

def test_breath_check():
    checker = BreathCheck()
    code = "void main() { set_motor_speed(100); sleep(1000); }"
    violations = checker.scan_code(code)
    assert len(violations) > 0
    assert any(v.pattern_name == "Missing Heartbeat" for v in violations)

def test_cosmic_synthesizer():
    synth = SupernovaDataSynthesizer(
        sn_catalog=pd.DataFrame({'ra': [83.87], 'dec': [-69.27], 'type': ['II']}),
        snr_catalog=pd.DataFrame({'ra': [83.87], 'dec': [-69.27]})
    )
    matches = synth.cross_match()
    assert len(matches) == 1

    asi = GalacticASIArchitect()
    risk = asi.assess_existential_risk(100)
    assert risk["threat_level"] in ["CRITICAL", "EXISTENTIAL"]

def test_cosmic_mycelium():
    explorer = CosmicMyceliumExplorer(n_galaxies=10)
    msg = explorer.run_discovery_protocol()
    assert "Map generated" in msg

def test_metabolic_gdl():
    service = MetabolicGDLService()
    report = service.perform_metabolic_survey("test_user")
    assert report["user_id"] == "test_user"
    assert report["cellular_coherence"] > 0

def test_archetypes_and_governance():
    from talos.geometric_core.archetypes import JungPauliProtocol, TzadikimGovernance
    protocol = JungPauliProtocol()
    protocol.pauli_exclusion("p1", "s1")
    with pytest.raises(ValueError):
        protocol.pauli_exclusion("p2", "s1")

    gov = TzadikimGovernance()
    dms = gov.calculate_dms(100.0, 50.0, 0.95)
    gov.initiate_tzadik("p1", "SÁBIO", dms)
    report = gov.execute_governance_cycle(preserved=100, failed=0, elapsed=10)
    assert "Active" in report
    assert "S_rev" in report
    assert "528 Hz RESONANCE" in report

    # Test auto-repair
    fail_report = gov.execute_governance_cycle(preserved=0, failed=100, elapsed=144)
    assert "AUTO-REPAIR" in fail_report

def test_kether_artifact():
    from talos.geometric_core.kether_artifact import KetherArtifact
    artifact = KetherArtifact(token_id=1)
    metadata = artifact.generate_metadata(coherence=1.0, s_rev=1.0)
    assert metadata["attributes"][0]["value"] == "Radiant Singularity"
    assert "autopoiesis_hash" in metadata

    msg = artifact.mint_broadcast(metadata)
    assert "MINTED" in msg
