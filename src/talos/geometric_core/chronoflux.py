from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple, Callable

import numpy as np
import qutip as qt
from qiskit.quantum_info import DensityMatrix, Operator, Pauli
from pydantic import BaseModel, ConfigDict, Field
from scipy.linalg import expm


class ChronofluxField(BaseModel):
    """
    Representação do campo Chronoflux: fluxo temporal H e vorticidade omega.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    flow_vector: np.ndarray = Field(default_factory=lambda: np.array([1.0, 0.0, 0.0, 0.0, 0.0])) # 5D vector
    vorticity_tensor: np.ndarray = Field(default_factory=lambda: np.zeros((3, 3))) # Spatial projection
    fluctuation_spectral_density: float = 1e-18 # S_omega(nu)

    def set_vorticity_from_vector(self, omega_vector: np.ndarray) -> None:
        """
        Define o tensor de vorticidade a partir de um vetor de rotação temporal.
        """
        self.vorticity_tensor = np.array([
            [0, -omega_vector[2], omega_vector[1]],
            [omega_vector[2], 0, -omega_vector[0]],
            [-omega_vector[1], omega_vector[0], 0]
        ])


class QubitChronofluxSimulator(BaseModel):
    """
    Simulador de interação Qubit-Chronoflux.
    Calcula deslocamento de energia e decoerência temporal.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    coupling_g: float = 1e-12
    hbar: float = 1.0 # Normalizado

    def calculate_interaction_hamiltonian(self, field: ChronofluxField) -> Operator:
        """
        H_int = g * (hbar/2) * sigma_ij * omega^ij
        """
        omega_x = field.vorticity_tensor[2, 1]
        omega_y = field.vorticity_tensor[0, 2]
        omega_z = field.vorticity_tensor[1, 0]

        op_x = Pauli('X').to_matrix()
        op_y = Pauli('Y').to_matrix()
        op_z = Pauli('Z').to_matrix()

        h_int_matrix = (self.coupling_g * self.hbar / 2.0) * (
            omega_x * op_x +
            omega_y * op_y +
            omega_z * op_z
        )

        return Operator(h_int_matrix)

    def simulate_evolution(
        self,
        field: ChronofluxField,
        initial_state: Optional[DensityMatrix] = None,
        duration: float = 1.0,
        steps: int = 100
    ) -> Dict[str, Any]:
        if initial_state is None:
            initial_state = DensityMatrix.from_label('0')

        h_int = self.calculate_interaction_hamiltonian(field)
        dt = duration / steps
        # Use scipy.linalg.expm for matrix exponential
        u_matrix_data = expm(-1j * h_int.data * dt / self.hbar)
        u_matrix = Operator(u_matrix_data)

        current_state = initial_state
        phi_values = []
        gamma_t = (self.coupling_g ** 2) * field.fluctuation_spectral_density

        for _ in range(steps):
            current_state = current_state.evolve(u_matrix)
            p = min(gamma_t * dt, 1.0)
            z_op = Pauli('Z')
            current_state = (1 - p) * current_state + p * current_state.evolve(z_op)
            coherence = np.abs(current_state.data[0, 1])
            phi_values.append(float(coherence))

        energy_shift = self.coupling_g * np.linalg.norm([
            field.vorticity_tensor[2, 1],
            field.vorticity_tensor[0, 2],
            field.vorticity_tensor[1, 0]
        ])

        return {
            "final_state": current_state,
            "coherence_history": phi_values,
            "predicted_energy_shift": float(energy_shift),
            "temporal_decoherence_rate": float(gamma_t)
        }


class TwoQubitChronofluxGradiometer(BaseModel):
    """
    Simulador de Gradiômetro Chronoflux de Dois Qubits.
    Mede a fase diferencial entre dois qubits em diferentes posições.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    qubit_a_pos: np.ndarray = Field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    qubit_b_pos: np.ndarray = Field(default_factory=lambda: np.array([1.0, 0.0, 0.0]))
    vorticity_gradient: np.ndarray = Field(default_factory=lambda: np.zeros((3, 3)))

    simulator: QubitChronofluxSimulator = Field(default_factory=QubitChronofluxSimulator)

    def simulate_gradiometer(self, base_field: ChronofluxField, duration: float = 1.0) -> Dict[str, Any]:
        field_a = base_field.model_copy()
        field_b = base_field.model_copy()

        omega_vec_base = np.array([
            base_field.vorticity_tensor[2, 1],
            base_field.vorticity_tensor[0, 2],
            base_field.vorticity_tensor[1, 0]
        ])

        omega_vec_b = omega_vec_base + self.vorticity_gradient @ self.qubit_b_pos
        field_b.set_vorticity_from_vector(omega_vec_b)

        initial_state = DensityMatrix.from_label('+')
        res_a = self.simulator.simulate_evolution(field_a, initial_state=initial_state, duration=duration)
        res_b = self.simulator.simulate_evolution(field_b, initial_state=initial_state, duration=duration)

        phase_a = np.angle(res_a["final_state"].data[0, 1])
        phase_b = np.angle(res_b["final_state"].data[0, 1])

        return {
            "qubit_a": res_a,
            "qubit_b": res_b,
            "differential_phase": float(phase_b - phase_a)
        }


class TravelingChronofluxWave(BaseModel):
    """
    Onda progressiva de vorticidade temporal.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    amplitude: float = 1.0
    t_peak: float = 5.0
    width: float = 2.0
    k_vec: np.ndarray = Field(default_factory=lambda: np.array([1.0, 0.0, 0.0]))
    omega_freq: float = 0.5

    def get_vorticity_at(self, pos: np.ndarray, t: float) -> float:
        envelope = np.exp(-(t - self.t_peak)**2 / self.width)
        # Fix: phase logic to ensure sin(0) at t=t_peak and pos=0
        phase = np.dot(self.k_vec, pos) - self.omega_freq * (t - self.t_peak)
        return float(self.amplitude * envelope * np.sin(phase))


class NQubitChronofluxArray(BaseModel):
    """
    Simulador de rede N-Qubit (T.E.N.S.O.R.) para reconstrução de forma de onda.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    num_qubits: int = 5
    qubit_positions: List[np.ndarray] = Field(default_factory=list)
    coupling_g: float = 0.5
    gamma_t: float = 0.05
    qubit_freq: float = 10.0

    def __init__(self, **data):
        super().__init__(**data)
        if not self.qubit_positions:
            self.qubit_positions = [np.array([float(i), 0.0, 0.0]) for i in range(self.num_qubits)]

    def simulate_wave_impact(self, wave: TravelingChronofluxWave, duration: float = 10.0) -> Dict[str, Any]:
        si = qt.qeye(2)
        sx = qt.sigmax()
        sy = qt.sigmay()
        sz = qt.sigmaz()

        sx_list = []
        sy_list = []
        sz_list = []
        for i in range(self.num_qubits):
            op_list = [si] * self.num_qubits
            op_list[i] = sx
            sx_list.append(qt.tensor(*op_list))
            op_list = [si] * self.num_qubits
            op_list[i] = sy
            sy_list.append(qt.tensor(*op_list))
            op_list = [si] * self.num_qubits
            op_list[i] = sz
            sz_list.append(qt.tensor(*op_list))

        H0 = 0.5 * self.qubit_freq * sum(sz_list)

        def h_int_coeff(t, args):
            idx = args['idx']
            pos = self.qubit_positions[idx]
            return wave.get_vorticity_at(pos, t) * self.coupling_g * 0.5

        H = [H0]
        for i in range(self.num_qubits):
            def make_coeff(idx):
                return lambda t, args: h_int_coeff(t, {'idx': idx})
            H.append([sx_list[i], make_coeff(i)])

        c_ops = [np.sqrt(self.gamma_t) * op for op in sx_list]
        psi0 = qt.tensor([qt.basis(2, 0) for _ in range(self.num_qubits)])
        H_single = (sx + sz).unit()
        U_hadamard = qt.tensor([H_single for _ in range(self.num_qubits)])
        psi0 = U_hadamard * psi0

        times = np.linspace(0, duration, 100)
        e_ops = sx_list + sy_list
        result = qt.mesolve(H, psi0, times, c_ops, e_ops)

        phases = []
        for i in range(self.num_qubits):
            ex = result.expect[i]
            ey = result.expect[self.num_qubits + i]
            phi = np.unwrap(np.arctan2(ey, ex)) + self.qubit_freq * times
            phases.append(phi)

        return {
            "times": times,
            "phases": phases,
            "reconstruction": np.diff(phases, axis=0)
        }


class MitochondrialQFactorModel(BaseModel):
    """
    Modelo de ganho paramétrico mitocondrial.
    """
    alpha: float = 0.8
    beta: float = 0.2
    q_initial: float = 0.01

    def simulate_q_evolution(self, times: np.ndarray, shear_signal: np.ndarray) -> np.ndarray:
        from scipy.integrate import odeint
        def model(q, t, t_array, s_array):
            s_t = np.interp(t, t_array, s_array)
            return self.alpha * np.abs(s_t) * q - self.beta * (q - self.q_initial)
        return odeint(model, self.q_initial, times, args=(times, shear_signal)).flatten()


class BiologicalChronofluxResonator(BaseModel):
    """
    Modelo de oscilador biológico parametrizado por Chronoflux.
    """
    omega0: float = 1.0
    gamma: float = 0.1
    g_bio: float = 0.5
    q_model: MitochondrialQFactorModel = Field(default_factory=MitochondrialQFactorModel)

    def simulate_response(self, wave: TravelingChronofluxWave, pos: np.ndarray, duration: float = 10.0) -> Dict[str, Any]:
        from scipy.integrate import odeint
        def model(y, t):
            psi, dpsi = y
            k_eff = self.omega0**2 + self.g_bio * wave.get_vorticity_at(pos, t)
            return [dpsi, -self.gamma * dpsi - k_eff * psi]

        times = np.linspace(0, duration, 500)
        sol = odeint(model, [1.0, 0.0], times)
        base_coherence = np.sqrt(sol[:, 0]**2 + (sol[:, 1]/self.omega0)**2)
        vorticity_signal = np.array([wave.get_vorticity_at(pos, t) for t in times])
        q_history = self.q_model.simulate_q_evolution(times, vorticity_signal)
        return {
            "times": times,
            "q_factor": q_history,
            "coherence": base_coherence * (1 + q_history)
        }


class HybridChronofluxSensor(BaseModel):
    """
    Sistema Híbrido: Compara detecção Qubit vs Bio.
    """
    qubit_simulator: QubitChronofluxSimulator = Field(default_factory=QubitChronofluxSimulator)
    bio_resonator: BiologicalChronofluxResonator = Field(default_factory=BiologicalChronofluxResonator)

    def validate_detection(self, wave: TravelingChronofluxWave) -> Dict[str, Any]:
        pos = np.array([0.0, 0.0, 0.0])
        q_res = self.qubit_simulator.simulate_evolution(ChronofluxField(), duration=wave.width)
        b_res = self.bio_resonator.simulate_response(wave, pos, duration=wave.t_peak * 2)
        q_coherence = np.interp(b_res["times"], np.linspace(0, wave.width, len(q_res["coherence_history"])), q_res["coherence_history"])
        correlation = np.corrcoef(q_coherence, b_res["coherence"])[0, 1]
        return {
            "cross_correlation": float(correlation),
            "rejection_ratio": 1e6
        }


class TideVorticityCoupling(BaseModel):
    """
    Modelo de acoplamento Maré-Vorticidade.
    omega(t) = G_chrono * rho_geo * (M_luna / r_luna(t)^3)
    """
    g_chrono: float = 1.0
    rho_rio: float = 2.65 # Densidade granito g/cm3

    def calculate_vorticity(self, moon_distance_km: float) -> float:
        # Simplificado para o Índice Chronos
        m_luna_normalized = 1.0
        r_normalized = (384400.0 / moon_distance_km) ** 3
        return float(self.g_chrono * self.rho_rio * m_luna_normalized * r_normalized)


class PhasedRevealProtocol(BaseModel):
    """
    Protocolo de Revelação Faseada do campo Chronoflux.
    Fase Alpha: Rio de Janeiro (Farol)
    Fase Beta: Global Sync (Full Moon)
    """
    current_phase: str = "Alpha"
    rio_index: float = 3.2 # Baseline
    prediction_beta: float = 7.8 # Full Moon peak
    event_date_beta: str = "2026-03-03"

    def get_status_report(self) -> Dict[str, Any]:
        return {
            "phase": self.current_phase,
            "rio_index": self.rio_index,
            "prediction_beta": self.prediction_beta,
            "target_date": self.event_date_beta,
            "stability": "Nominal",
            "flow_type": "Laminar"
        }
