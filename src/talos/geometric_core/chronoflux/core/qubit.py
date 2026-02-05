"""
Implements the qubit interaction with Chronoflux field ω_μν.
Solves the Lindblad master equation with H_int = g(ħ/2) σ·ω coupling.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import numpy as np
import qutip as qt
from pydantic import BaseModel, ConfigDict, Field
from qiskit.quantum_info import DensityMatrix, Operator, Pauli
from scipy.linalg import expm

from talos.geometric_core.chronoflux.core.field import ChronofluxField


class ChronofluxQubit(BaseModel):
    """
    A qubit sensor coupled to the Chronoflux temporal vorticity field.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    position: np.ndarray = Field(default_factory=lambda: np.zeros(3))  # 3D spatial position
    g: float = 1e-5
    hbar: float = 1.0

    def interaction_hamiltonian(self, omega_tensor: np.ndarray) -> qt.Qobj:
        """
        Build H_int = g(ħ/2) ∑_{ij} σ_ij ω^{ij} for the qubit.
        """
        # Extract spatial components (1,2,3 correspond to x,y,z)
        omega_xy = omega_tensor[1, 2]
        omega_xz = omega_tensor[1, 3]
        omega_yz = omega_tensor[2, 3]

        sx = qt.sigmax()
        sy = qt.sigmay()
        sz = qt.sigmaz()

        H_int = self.g * (self.hbar / 2) * (omega_xy * sx + omega_yz * sy + omega_xz * sz)

        return H_int

    def evolve_with_chronoflux(
        self,
        H0: qt.Qobj,
        omega_field: Callable[[float, np.ndarray], np.ndarray],
        times: np.ndarray,
        decoherence_rate: float = 0.01,
    ) -> tuple[Any, dict[str, np.ndarray]]:
        """
        Solve master equation for qubit in Chronoflux field.
        """
        # Initial state: |+⟩
        psi0 = (qt.basis(2, 0) + qt.basis(2, 1)).unit()

        # Static part
        sx = qt.sigmax()
        sy = qt.sigmay()
        sz = qt.sigmaz()

        # We need to construct the time-dependent interaction properly for QuTiP
        # H(t) = H0 + sum_i coeff_i(t) * Pauli_i

        def H_int_coeff_xy(t, args):
            omega_t = omega_field(t, self.position)
            return omega_t[1, 2] * self.g * (self.hbar / 2)

        def H_int_coeff_yz(t, args):
            omega_t = omega_field(t, self.position)
            return omega_t[2, 3] * self.g * (self.hbar / 2)

        def H_int_coeff_xz(t, args):
            omega_t = omega_field(t, self.position)
            return omega_t[1, 3] * self.g * (self.hbar / 2)

        H = [H0, [sx, H_int_coeff_xy], [sy, H_int_coeff_yz], [sz, H_int_coeff_xz]]

        # Lindblad decoherence (dephasing along Z)
        c_ops = [np.sqrt(decoherence_rate) * sz]

        # Solve master equation
        result = qt.mesolve(H, psi0, times, c_ops)

        # Calculate expectation values
        expectations = {
            "sigma_x": qt.expect(sx, result.states),
            "sigma_y": qt.expect(sy, result.states),
            "sigma_z": qt.expect(sz, result.states),
        }

        return result, expectations


class QubitChronofluxSimulator(BaseModel):
    """
    Simulador de interação Qubit-Chronoflux.
    Calcula deslocamento de energia e decoerência temporal.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    coupling_g: float = 1e-12
    hbar: float = 1.0  # Normalizado

    def calculate_interaction_hamiltonian(self, field: ChronofluxField) -> Operator:
        """
        H_int = g * (hbar/2) * sigma_ij * omega^ij
        """
        omega_x = field.vorticity_tensor[2, 1]
        omega_y = field.vorticity_tensor[0, 2]
        omega_z = field.vorticity_tensor[1, 0]

        op_x = Pauli("X").to_matrix()
        op_y = Pauli("Y").to_matrix()
        op_z = Pauli("Z").to_matrix()

        h_int_matrix = (self.coupling_g * self.hbar / 2.0) * (omega_x * op_x + omega_y * op_y + omega_z * op_z)

        return Operator(h_int_matrix)

    def simulate_evolution(
        self,
        field: ChronofluxField,
        initial_state: Optional[DensityMatrix] = None,
        duration: float = 1.0,
        steps: int = 100,
    ) -> Dict[str, Any]:
        if initial_state is None:
            initial_state = DensityMatrix.from_label("0")

        h_int = self.calculate_interaction_hamiltonian(field)
        dt = duration / steps
        # Use scipy.linalg.expm for matrix exponential
        u_matrix_data = expm(-1j * h_int.data * dt / self.hbar)
        u_matrix = Operator(u_matrix_data)

        current_state = initial_state
        phi_values = []
        gamma_t = (self.coupling_g**2) * field.fluctuation_spectral_density

        for _ in range(steps):
            current_state = current_state.evolve(u_matrix)
            p = min(gamma_t * dt, 1.0)
            z_op = Pauli("Z")
            current_state = (1 - p) * current_state + p * current_state.evolve(z_op)
            coherence = np.abs(current_state.data[0, 1])
            phi_values.append(float(coherence))

        energy_shift = self.coupling_g * np.linalg.norm(
            [field.vorticity_tensor[2, 1], field.vorticity_tensor[0, 2], field.vorticity_tensor[1, 0]]
        )

        return {
            "final_state": current_state,
            "coherence_history": phi_values,
            "predicted_energy_shift": float(energy_shift),
            "temporal_decoherence_rate": float(gamma_t),
        }
