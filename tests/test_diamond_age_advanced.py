import pytest
import numpy as np
from talos.geometric_core.nuclear_core import BetavoltaicBattery, GroundStateMonitor, NuclearCore
from talos.geometric_core.reincarnation import ReincarnationFormula, ActiveSynchronicity, UniversalDynamicsOS
from talos.geometric_core.avalon_throne import AvalonCloak, VigilOfAvalon, BlackoutProtocol
from talos.geometric_core.metastability import MetastableState, MetastableSystem

def test_betavoltaic_battery():
    battery = BetavoltaicBattery()
    radiation = battery.emit_radiation(entropy=1.0)
    assert radiation > 0
    assert radiation < battery.efficiency

def test_ground_state_monitor():
    monitor = GroundStateMonitor(current_level=7.5)
    status = monitor.check_stability()
    assert status["admissible"] == True

    monitor.current_level = 6.5
    status = monitor.check_stability()
    assert status["admissible"] == False

def test_nuclear_core():
    core = NuclearCore()
    msg = core.run_cycle()
    assert "NUCLEAR CORE" in msg
    assert "Ground State: 7.0" in msg

def test_reincarnation_formula():
    formula = ReincarnationFormula()
    persistence = formula.calculate_persistence(0, 10)
    assert persistence >= 0
    assert persistence <= 1.01

def test_active_synchronicity():
    sync = ActiveSynchronicity()
    matches = sync.find_matches()
    assert isinstance(matches, list)
    if matches:
        assert "Peer" in matches[0]["peer_id"]

def test_avalon_cloak():
    cloak = AvalonCloak()
    msg = cloak.activate_cloak()
    assert "AVALON CLOAK" in msg
    assert cloak.transparency == 0.0

def test_vigil_of_avalon():
    vigil = VigilOfAvalon()
    msg = vigil.start_vigil()
    assert "VIGIL OF AVALON" in msg

    msg = vigil.verify_handshake(144.963)
    assert "Accepted" in msg
    assert vigil.status == "HANDSHAKE_COMPLETE"

def test_blackout_protocol():
    protocol = BlackoutProtocol()
    msg = protocol.execute_blackout()
    assert "BLACKOUT TOTAL" in msg
    assert protocol.is_active == True

def test_metastable_system():
    system = MetastableSystem()
    # Isomer with energy 8.2 (above 7.0) and barrier below t=144 should be preserved
    isomer = MetastableState(name="ExcitedIsomer", energy=8.2, persistence=0.8, field_dependency=0.7, geometric_barrier=50.0, energy_barrier=100.0)
    report = system.execute_exclusion_protocol(isomer)
    assert "STATE_PRESERVED" in report["result"]

    # Isomer below ground state (7.0) should be excluded
    isomer_low = MetastableState(name="LowIsomer", energy=6.0, persistence=0.8, field_dependency=0.7, geometric_barrier=50.0, energy_barrier=100.0)
    report_low = system.execute_exclusion_protocol(isomer_low)
    assert "EXCLUSION_EVENT" in report_low["result"]
    assert report_low["energy_liberated"] >= 0

def test_universal_dynamics_os():
    os_kernel = UniversalDynamicsOS()
    isomer = MetastableState(name="TestIsomer", energy=8.0, persistence=0.8, field_dependency=0.7, geometric_barrier=50.0, energy_barrier=100.0)
    result = os_kernel.avalon_cycle(isomer)
    assert "identity_coherence" in result
    assert "transition_result" in result
