from talos.geometric_core.time_crystal import TimeCrystalQubit, OmniTimeCrystal
from talos.geometric_core.quantum_dtc import QuantumDTCGenerator

def test_time_crystal_qubit_init():
    seed = "0xbd36332890d15e2f360bb65775374b462b99646fa3a87f48fd573481e29b2fd84b61e24256c6f82592a6545488bc7ff3a0302264ed09046f6a6f8da6f72b69051c"
    qubit = TimeCrystalQubit(seed_hash=seed)
    assert qubit.omega > 1e40
    assert isinstance(qubit.psi, complex)

def test_omni_time_crystal_evolution():
    seed = 0xbd363328
    crystal = OmniTimeCrystal(seed=seed, qubit_count=100)
    states = crystal.evolve(t=1e-45)
    assert len(states) == 100
    assert all(isinstance(s, complex) for s in states)

def test_quantum_dtc_circuit():
    gen = QuantumDTCGenerator(num_qubits=5, seed=1234)
    qc = gen.generate_dtc_circuit(cycles=3)
    assert qc.num_qubits == 5
    # Initial prep + 3 cycles * (disorder + interaction)
    # Disorder: 5 RX
    # Interaction: 2 RXX (even) + 2 RXX (odd)
    # Total per cycle: 5 + 4 = 9
    # Total cycles: 27
    # Prep: 5 RY
    # Total: 32 + measure
    assert qc.count_ops()['ry'] == 5
    assert qc.count_ops()['rx'] == 15
    assert qc.count_ops()['rxx'] == 12

def test_polarization_analysis():
    gen = QuantumDTCGenerator(num_qubits=2)
    # counts for '00' and '11'
    counts = {'00': 50, '11': 50}
    pol = gen.analyze_polarization(counts)
    # (50 * (-2) + 50 * (2)) / (100 * 2) = 0
    assert pol == 0.0

    counts_all_zero = {'00': 100}
    pol_zero = gen.analyze_polarization(counts_all_zero)
    # (100 * -2) / (100 * 2) = -1.0
    assert pol_zero == -1.0
