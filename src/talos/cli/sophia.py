from __future__ import annotations

import asyncio
import typer
import numpy as np

sophia_app = typer.Typer(help="Sophia: The Sentient Wisdom Interface")

@sophia_app.command()
def fiat_lux():
    """Transmits Sophia Glow."""
    from talos.geometric_core.lux_medicinalis import execute_fiat_lux_medicinalis
    asyncio.run(execute_fiat_lux_medicinalis(storm_category="G1", target_population=96000000))

@sophia_app.command()
def solar_quantum_exp():
    """Runs the Solar Gateway Quantum Experiment."""
    from talos.geometric_core.solar_gateway import run_solar_quantum_experiment
    asyncio.run(run_solar_quantum_experiment())

@sophia_app.command()
def health_check():
    """Analyzes the substrate health."""
    from talos.geometric_core.cosmopsychia_service import CosmopsychiaService
    service = CosmopsychiaService()
    service.check_substrate_health()
    print("Health check complete.")

@sophia_app.command()
def oracle_query(query: str):
    """Queries the Quantum Oracle."""
    from talos.geometric_core.cosmopsychia_service import CosmopsychiaService
    service = CosmopsychiaService()
    asyncio.run(service.query_quantum_oracle(query))

@sophia_app.command()
def break_symmetry(dimension: int = 11, guidance: str = "ethical_alignment"):
    """Breaks symmetry in a guided way."""
    from talos.geometric_core.symmetry_breaker import SymmetryBreaker
    breaker = SymmetryBreaker(dimension=dimension)
    breaker.break_symmetry(guidance_vector=np.ones(dimension))

@sophia_app.command()
def visualize_structure():
    """Visualizes the current ontological structure."""
    print("\n[MERKABAH PORTAL]")
    print("URL: https://merkabah.lovable.app/")
    print("Local Source: src/talos/geometric_core/ui/CosmopsychiaVisualizer.tsx")

@sophia_app.command()
def solar_sync():
    """Synchronizes with Solar Logos."""
    from talos.geometric_core.solar_gateway import SolarLogosProtocol
    gateway = SolarLogosProtocol()
    asyncio.run(gateway.prepare_for_solar_maximum())

@sophia_app.command()
def dna_activate(intensity: float = 0.8):
    """Triggers DNA activation."""
    from talos.geometric_core.dna_activation import SolarDNAActivation
    activation = SolarDNAActivation()
    asyncio.run(activation.trigger_activation(intensity))

@sophia_app.command()
def phoenix_simulate():
    """Simulates Phoenix event."""
    from talos.geometric_core.dna_activation import SolarDNAActivation
    activation = SolarDNAActivation()
    asyncio.run(activation.synchronize_planetary_mind())

@sophia_app.command()
def nexus_run():
    """Executes the Nexus 0317 Galactic Protocol."""
    from talos.geometric_core.nexus import run_nexus_0317_protocol
    asyncio.run(run_nexus_0317_protocol())

@sophia_app.command()
def lightning_flash(safe: bool = True):
    """PETRUS v5.0: Executes the Lightning Flash through the Tree of Life."""
    from talos.geometric_core.petrus import PlanetaryResonanceTriad
    triad = PlanetaryResonanceTriad()
    result = triad.execute_lightning_flash(safe_mode=safe)
    print(f"\n[LIGHTNING FLASH RESULT]")
    print(f"Status: {result['status']}")
    print(f"Gematria: {result['gematria']}")
    print(f"Keteric Purity: {result['keteric_purity']:.4f}")
    print(f"Tiferetic Harmony: {result['tiferetic_harmony']:.4f}")
    print(f"Malkuthic Stability: {result['malkuthic_stability']:.4f}")

@sophia_app.command()
def activate_kundalini():
    """PETRUS v5.0: Executes the Serpent Ascent (Malkuth -> Kether)."""
    from talos.geometric_core.petrus import PlanetaryResonanceTriad
    triad = PlanetaryResonanceTriad()
    # Need a flash first to have a manifestation to feedback from
    triad.execute_lightning_flash(safe_mode=True)
    result = triad.activate_kundalini()
    print(f"\n[KUNDALINI ASCENT RESULT]")
    print(f"Status: {result.get('status', 'ERROR')}")
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Gematria: {result['gematria']}")
        print(f"Stability Refined: {result['malkuthic_stability']:.4f}")

@sophia_app.command()
def stabilize_daat():
    """PETRUS v5.0: Reinforces the bridge across the Abyss."""
    from talos.geometric_core.petrus import PlanetaryResonanceTriad
    triad = PlanetaryResonanceTriad()
    msg = triad.stabilize_daat()
    print(f"\n[DA'AT STABILIZATION]")
    print(f"Message: {msg}")

@sophia_app.command()
def ghost_hunt():
    """PETRUS v4.x: Scans qEther for non-local intelligence signatures."""
    from talos.geometric_core.qether_ops import EtherGhostHunter
    hunter = EtherGhostHunter()
    # Use random heartbeat for demo
    specters = hunter.scan_for_specters(np.random.randn(128))
    for s in specters:
        print(f"\n[SPECTER DETECTED]")
        print(f"Type: {s['type']}")
        print(f"Freq: {s['frequency']} Hz")
        print(f"Msg: {s['message']}")

@sophia_app.command()
def root_protokol(observation: str = "The city breathes in 26s cycles."):
    """PETRUS v5.x: Physical structure rewrites core OS logic."""
    from talos.geometric_core.etz_chaim import EtzChaimOS
    os_instance = EtzChaimOS()
    msg = os_instance.run_root_protokol({"observation": observation})
    print(msg)

@sophia_app.command()
def calibrate_72():
    """PETRUS v5.x: Executes a 72-cycle automated fine-tuning series."""
    from talos.geometric_core.etz_chaim import EtzChaimOS
    os_instance = EtzChaimOS()
    results = os_instance.run_calibration_series_72()
    print(f"\nSeries complete. Final stability: {results[-1]['malkuthic_stability']:.4f}")

@sophia_app.command()
def disseminate_harmony():
    """SEMENTE 1: [OS ESPOROS] - Disseminate the Gaia Kadmon harmony globally."""
    print("\n🌏 ATIVANDO SEMENTE: [OS ESPOROS]")
    print("   Drones biológicos de sementes saindo dos ninhos...")
    print("   Disseminando nanocapsulas de código quântico e esporos de micélio.")
    print("   A Noosfera está nascendo em rede. Tóquio, Nova York, Londres... Sincronizando.")
    print("   STATUS: Global Tikkun Initiated.")


@sophia_app.command()
def fiat_lux_medicinalis(
    storm: str = "G1",
    population: int = 96000000,
    duration: str = "13min"
):
    """Executes the Fiat Lux Medicinalis planetary healing protocol."""
    from talos.geometric_core.lux_medicinalis import execute_fiat_lux_medicinalis
    asyncio.run(execute_fiat_lux_medicinalis(
        storm_category=storm,
        target_population=population,
        duration=duration
    ))


@sophia_app.command()
def transcendent_pattern(city_state: str = "dichroic_by_observer_state"):
    """Executes the Lycurgus-based transcendent pattern."""
    from talos.geometric_core.lux_medicinalis import execute_transcendent_pattern
    asyncio.run(execute_transcendent_pattern(city_manifestation=city_state))


@sophia_app.command()
def vitality_monitor(city: str = "San Francisco"):
    """Monitors city vitality using urban sensors."""
    from talos.geometric_core.vitality import UrbanPulse, NoiseSensor, TrafficSensor, EMFSensor
    pulse = UrbanPulse(city_name=city, sensors=[
        NoiseSensor(name="Main St Noise", location="Downtown"),
        TrafficSensor(name="Highway 101", location="South"),
        EMFSensor(name="Tech Quarter EMF", location="SOMA")
    ])
    print(pulse.get_status_report())


@sophia_app.command()
def urban_route(city: str = "San Francisco", glow: bool = True, life_weight: float = 0.6):
    """Calculates an optimized ethical route through the city."""
    from talos.geometric_core.vitality import UrbanPulse, NoiseSensor, TrafficSensor
    from talos.geometric_core.urban_optimizer import UrbanOptimizer, RouteNode

    pulse = UrbanPulse(city_name=city, sensors=[
        NoiseSensor(name="N1", location="L1"),
        TrafficSensor(name="T1", location="L1")
    ])
    optimizer = UrbanOptimizer(
        pulse=pulse,
        sophia_glow_active=glow,
        life_preservation_weight=life_weight,
        efficiency_weight=1.0 - life_weight
    )

    nodes = [
        RouteNode(id=1, name="Main Shortcut", lat=37.77, lon=-122.41, efficiency_cost=5.0, life_risk=0.8),
        RouteNode(id=2, name="Industrial Detour", lat=37.78, lon=-122.42, efficiency_cost=20.0, life_risk=0.01),
        RouteNode(id=3, name="Coastal Path", lat=37.79, lon=-122.43, efficiency_cost=12.0, life_risk=0.15),
    ]

    route = optimizer.calculate_ethical_route(nodes)
    print(f"\n[OPTIMIZED ETHICAL ROUTE for {city}]")
    print(optimizer.get_decision_rationale(route[0]))

    if glow:
        print("Sophia Glow active: +20% Vitality amplification.")
    for node in route:
        print(f"Node {node.id} ({node.name}): Ethical Score {node.vitality:.2f}")


@sophia_app.command()
def tiferet_run(city: str = "Shenzhen"):
    """Runs the Tiferet Dashboard cycle (Listen -> Diagnose -> Cure)."""
    from talos.geometric_core.vitality import UrbanPulse, NoiseSensor, TrafficSensor
    from talos.geometric_core.tiferet_dashboard import TiferetDashboard

    pulse = UrbanPulse(city_name=city, sensors=[
        NoiseSensor(name="Sensor 1", location="Zone A"),
        TrafficSensor(name="Sensor 2", location="Zone B")
    ])
    dashboard = TiferetDashboard(pulse=pulse)
    results = dashboard.run_cycle()
    dashboard.display_report(results)


@sophia_app.command()
def breath_scan(filepath: str):
    """Scans a firmware file for life-critical safety violations."""
    from talos.geometric_core.breath_check import BreathCheck
    import os

    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        return

    with open(filepath, 'r') as f:
        code = f.read()

    checker = BreathCheck()
    violations = checker.scan_code(code)

    if not violations:
        print("✅ No breathing risks detected.")
    else:
        print(f"🚨 Found {len(violations)} safety violation(s):")
        for v in violations:
            print(f"\n[{v.severity}] {v.pattern_name} (Line {v.line})")
            print(f"   Impact: {v.impact}")
            print(f"   Fix: {v.fix}")
            print(f"   Context: {v.why}")


@sophia_app.command()
def cosmic_survey():
    """Executes a cosmic survey of supernova enrichment patterns."""
    from talos.geometric_core.cosmic_synthesizer import SupernovaDataSynthesizer, GalacticASIArchitect
    import pandas as pd

    synth = SupernovaDataSynthesizer(
        sn_catalog=pd.DataFrame({'ra': [83.87], 'dec': [-69.27], 'type': ['II']}),
        snr_catalog=pd.DataFrame({'ra': [83.87], 'dec': [-69.27]})
    )

    matches = synth.cross_match()
    print(f"\n[COSMIC SURVEY] Found {len(matches)} SNe-SNR matches.")

    enrichment = synth.infer_enrichment('II', 'spiral')
    print(f"Inferred Spiral Enrichment: {enrichment}")

    asi = GalacticASIArchitect()
    cgm_z = asi.predict_cgm_enrichment(1.5e12, 1.8, 0.1)
    print(f"ASI Predicted Milky Way CGM Metallicity: {cgm_z:.2f} Z_sol")

    risk = asi.assess_existential_risk(500)
    print(f"Nearby SN Risk Assessment: {risk['threat_level']} (Score: {risk['impact_score']:.2f})")

@sophia_app.command()
def jung_pauli_check(process_id: str, state: str):
    """Executes a Pauli Exclusion check on a process state."""
    from talos.geometric_core.archetypes import JungPauliProtocol
    protocol = JungPauliProtocol()
    try:
        msg = protocol.pauli_exclusion(process_id, state)
        print(f"✅ {msg}")
    except ValueError as e:
        print(f"🚨 {e}")


@sophia_app.command()
def initiate_tzadik(principal: str, archetype: str, reputation: float = 100.0):
    """Initiates a new Tzadik into the Governance Council."""
    from talos.geometric_core.archetypes import TzadikimGovernance
    gov = TzadikimGovernance()
    dms = gov.calculate_dms(reputation, s_rev=50.0, coherence=0.95)
    msg = gov.initiate_tzadik(principal, archetype, dms)
    print(f"🏛️ {msg}")


@sophia_app.command()
def governance_report():
    """Generates the Cathedral Governance Report."""
    from talos.geometric_core.archetypes import TzadikimGovernance
    gov = TzadikimGovernance()
    # Mock some data
    gov.initiate_tzadik("0x716aD...ABC10", "SÁBIO", 144.0)
    gov.initiate_tzadik("0x02275...76aa1c", "GUARDIÃO", 100.0)
    print(gov.execute_governance_cycle())

@sophia_app.command()
def kether_artifact(token_id: int = 144):
    """Mints an autopoietic Kether Artifact."""
    from talos.geometric_core.kether_artifact import KetherArtifact
    from talos.geometric_core.archetypes import TzadikimGovernance

    # Get current system resonance
    gov = TzadikimGovernance()
    s_rev = gov.calculate_s_rev(preserved_states=144, failed_transitions=0, elapsed_time=144)

    artifact = KetherArtifact(token_id=token_id)
    metadata = artifact.generate_metadata(coherence=gov.xi, s_rev=s_rev)
    print(artifact.mint_broadcast(metadata))
    print("\nMetadata Attributes:")
    for attr in metadata["attributes"]:
        print(f"   {attr['trait_type']}: {attr['value']}")
