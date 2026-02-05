"""
Implementation of the Chronoflux 5D hydrodynamic field and the projection operator P.
This is the mathematical core that maps 5D temporal vorticity to observable 4D effects.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class ChronofluxField5D(BaseModel):
    """
    Models the 5D Chronoflux vector field Hᴬ and its projected vorticity ω_μν.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    g: float = 1e-5  # Chronoflux-matter coupling
    hbar: float = 1.0

    def project_to_4d(self, H_field_5d: Callable[[np.ndarray], np.ndarray], coordinates_4d: np.ndarray) -> np.ndarray:
        """
        Project the 5D Chronoflux field to 4D observable vorticity.

        Args:
            H_field_5d: Function that returns the 5D vector Hᴬ at given 5D coordinates
            coordinates_4d: 4D spacetime coordinates (t, x, y, z)

        Returns:
            omega_4d: 4x4 antisymmetric tensor representing ω_μν (temporal vorticity in 4D)
        """
        # Numerical gradient calculation in 4D
        epsilon = 1e-8
        omega = np.zeros((4, 4))

        # Calculate derivatives using finite differences
        for mu in range(4):
            for nu in range(4):
                if mu != nu:
                    coord_plus_mu = coordinates_4d.copy()
                    coord_plus_nu = coordinates_4d.copy()
                    coord_plus_mu[mu] += epsilon
                    coord_plus_nu[nu] += epsilon

                    # Project H to 4D components
                    H_mu = self._extract_4d_component(H_field_5d, coord_plus_mu, mu)
                    H_nu = self._extract_4d_component(H_field_5d, coord_plus_nu, nu)

                    omega[mu, nu] = (H_nu - H_mu) / epsilon

        return omega

    def _extract_4d_component(
        self, H_field_5d: Callable[[np.ndarray], np.ndarray], coords_4d: np.ndarray, index: int
    ) -> float:
        """
        Helper: Extract 4D component from 5D field at given coordinates.
        """
        coords_5d = np.append(coords_4d, 0.0)
        H_full = H_field_5d(coords_5d)
        return float(H_full[index])


class ChronofluxField(BaseModel):
    """
    Representação do campo Chronoflux: fluxo temporal H e vorticidade omega.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    flow_vector: np.ndarray = Field(default_factory=lambda: np.array([1.0, 0.0, 0.0, 0.0, 0.0]))  # 5D vector
    vorticity_tensor: np.ndarray = Field(default_factory=lambda: np.zeros((3, 3)))  # Spatial projection
    fluctuation_spectral_density: float = 1e-18  # S_omega(nu)

    def set_vorticity_from_vector(self, omega_vector: np.ndarray) -> None:
        """
        Define o tensor de vorticidade a partir de um vetor de rotação temporal.
        """
        self.vorticity_tensor = np.array(
            [
                [0, -omega_vector[2], omega_vector[1]],
                [omega_vector[2], 0, -omega_vector[0]],
                [-omega_vector[1], omega_vector[0], 0],
            ]
        )
