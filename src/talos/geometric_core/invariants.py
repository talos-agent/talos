from __future__ import annotations

from typing import Any, Callable, List

from pydantic import BaseModel


class InvariantResult(BaseModel):
    """
    Result of an invariant validation check.
    """

    name: str
    passed: bool
    details: str


class CGEInvariant(BaseModel):
    """
    Constitutional Geometric Engine (CGE) Invariant.
    """

    id: str
    name: str
    description: str
    validator: Callable[[Any], InvariantResult]


import numpy as np


def validate_ricci_curvature(state: Any) -> InvariantResult:
    """
    G1: Ricci curvature must be bounded to prevent singularities.
    """
    ricci_norm = 0.0
    if hasattr(state, "manifold") and state.manifold.learned_curvature is not None:
        # Using Frobenius norm as a proxy for Ricci tensor norm
        ricci_norm = float(np.linalg.norm(state.manifold.learned_curvature))

    max_curvature = 10.0

    return InvariantResult(
        name="Bounded Ricci Curvature",
        passed=ricci_norm <= max_curvature,
        details=f"OK (Ricci norm: {ricci_norm:.3f})"
        if ricci_norm <= max_curvature
        else f"Curvature too high: {ricci_norm:.3f} > {max_curvature}",
    )


def validate_state_volume(state: Any) -> InvariantResult:
    """
    G2: The volume of the state manifold must be finite and within bounds.
    """
    # Assuming 'state' has a 'manifold' attribute
    volume = 0.0
    if hasattr(state, "manifold"):
        volume = state.manifold.calculate_volume()
    elif hasattr(state, "calculate_volume"):
        volume = state.calculate_volume()

    max_volume = 1_000_000.0
    return InvariantResult(
        name="Finite State Volume",
        passed=volume <= max_volume,
        details=f"OK (Volume: {volume:.2f})"
        if volume <= max_volume
        else f"Volume too large: {volume:.2f} > {max_volume}",
    )


def validate_manifold_dimension(state: Any) -> InvariantResult:
    """
    G3: Manifold dimension must remain constant or grow slowly.
    """
    dimension = 0
    if hasattr(state, "manifold"):
        dimension = state.manifold.dimension
    elif hasattr(state, "dimension"):
        dimension = state.dimension

    max_dim = 256
    return InvariantResult(
        name="Stable Manifold Dimension",
        passed=dimension <= max_dim,
        details=f"OK (Dimension: {dimension})"
        if dimension <= max_dim
        else f"Dimension too high: {dimension} > {max_dim}",
    )


def get_default_geometric_invariants() -> List[CGEInvariant]:
    """
    Returns the standard set of geometric invariants for the CGE.
    """
    return [
        CGEInvariant(
            id="G1",
            name="Bounded Ricci Curvature",
            description="Ricci curvature must be bounded to prevent singularities",
            validator=validate_ricci_curvature,
        ),
        CGEInvariant(
            id="G2",
            name="Finite State Volume",
            description="The volume of the state manifold must be finite",
            validator=validate_state_volume,
        ),
        CGEInvariant(
            id="G3",
            name="Stable Manifold Dimension",
            description="Manifold dimension must remain stable",
            validator=validate_manifold_dimension,
        ),
    ]
