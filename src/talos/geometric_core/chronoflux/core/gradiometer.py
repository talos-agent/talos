"""
Implements N-qubit array and shear wave reconstruction for Chronoflux detection.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import numpy as np
import qutip as qt
from pydantic import BaseModel, ConfigDict, Field
from qiskit.quantum_info import DensityMatrix

from talos.geometric_core.chronoflux.core.field import ChronofluxField
from talos.geometric_core.chronoflux.core.qubit import QubitChronofluxSimulator
from talos.geometric_core.chronoflux.core.wave import TravelingChronofluxWave


class ChronofluxGradiometer(BaseModel):
    """
    An array of qubits designed to detect spatial gradients (shear) in the Chronoflux field.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    num_qubits: int = 5
    spacing: float = 1.0
    qubit_positions: List[np.ndarray] = Field(default_factory=list)
    g: float = 0.5
    hbar: float = 1.0

    def __init__(self, **data):
        super().__init__(**data)
        if not self.qubit_positions:
            self.qubit_positions = [np.array([float(i) * self.spacing, 0.0, 0.0]) for i in range(self.num_qubits)]

    def simulate_wave_propagation(
        self, wave_func: Callable[[np.ndarray, float], float], duration: float = 10.0
    ) -> Dict[str, Any]:
        """
        Simulates a traveling shear wave passing through the array.
        """
        si = qt.qeye(2)
        sx = qt.sigmax()
        sz = qt.sigmaz()
        sy = qt.sigmay()

        sx_list = []
        sy_list = []
        sz_list = []

        for i in range(self.num_qubits):
            op_list_x = [si] * self.num_qubits
            op_list_x[i] = sx
            sx_list.append(qt.tensor(*op_list_x))

            op_list_y = [si] * self.num_qubits
            op_list_y[i] = sy
            sy_list.append(qt.tensor(*op_list_y))

            op_list_z = [si] * self.num_qubits
            op_list_z[i] = sz
            sz_list.append(qt.tensor(*op_list_z))

        # Base Hamiltonian
        w_q = 10.0
        H0 = 0.5 * w_q * sum(sz_list)

        # Interaction
        H = [H0]
        for i in range(self.num_qubits):

            def make_coeff(idx):
                return lambda t, args: wave_func(self.qubit_positions[idx], t) * self.g * 0.5

            H.append([sx_list[i], make_coeff(i)])

        times = np.linspace(0, duration, 100)
        c_ops = [np.sqrt(0.01) * op for op in sx_list]

        # Initial state
        psi0 = qt.tensor([qt.basis(2, 0) for _ in range(self.num_qubits)])
        H_single = (sx + sz).unit()
        U_hadamard = qt.tensor([H_single for _ in range(self.num_qubits)])
        psi0 = U_hadamard * psi0

        result = qt.mesolve(H, psi0, times, c_ops, sx_list + sy_list)

        phases = []
        for i in range(self.num_qubits):
            ex = result.expect[i]
            ey = result.expect[self.num_qubits + i]
            phi = np.unwrap(np.arctan2(ey, ex)) + w_q * times
            phases.append(phi)

        return {"times": times, "phases": phases, "shear_map": np.diff(phases, axis=0)}


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

        omega_vec_base = np.array(
            [base_field.vorticity_tensor[2, 1], base_field.vorticity_tensor[0, 2], base_field.vorticity_tensor[1, 0]]
        )

        omega_vec_b = omega_vec_base + self.vorticity_gradient @ self.qubit_b_pos
        field_b.set_vorticity_from_vector(omega_vec_b)

        initial_state = DensityMatrix.from_label("+")
        res_a = self.simulator.simulate_evolution(field_a, initial_state=initial_state, duration=duration)
        res_b = self.simulator.simulate_evolution(field_b, initial_state=initial_state, duration=duration)

        phase_a = np.angle(res_a["final_state"].data[0, 1])
        phase_b = np.angle(res_b["final_state"].data[0, 1])

        return {"qubit_a": res_a, "qubit_b": res_b, "differential_phase": float(phase_b - phase_a)}


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
            idx = args["idx"]
            pos = self.qubit_positions[idx]
            return wave.get_vorticity_at(pos, t) * self.coupling_g * 0.5

        H = [H0]
        for i in range(self.num_qubits):

            def make_coeff(idx):
                return lambda t, args: h_int_coeff(t, {"idx": idx})

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

        return {"times": times, "phases": phases, "reconstruction": np.diff(phases, axis=0)}
