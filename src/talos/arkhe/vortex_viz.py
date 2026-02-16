"""
Arkhe(n) Vortex Visualization.
Generates the phase density plot for an OAM vortex handover.
Used to validate the purity of directional emissions.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np


def generate_vortex_plot(l_charge: int = 1, resolution: int = 200, output_path: str = "vortex_phase.png") -> None:
    """
    Generates a polar plot of the phase density of an OAM vortex.
    """
    print(f"Generating OAM Vortex Phase Density plot (l={l_charge})...")

    x = np.linspace(-2, 2, resolution)
    y = np.linspace(-2, 2, resolution)
    X, Y = np.meshgrid(x, y)

    # Convert to polar coordinates
    R = np.sqrt(X**2 + Y**2)
    Phi = np.arctan2(Y, X)

    # Calculate complex field: A(r) * exp(i * l * Phi)
    # Amplitude: ring-like for vortex (R * exp(-R^2))
    amplitude = R * np.exp(-(R**2))
    phase = np.angle(np.exp(1j * l_charge * Phi))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # 1. Phase Plot
    im1 = ax1.imshow(phase, extent=[-2, 2, -2, 2], cmap='twilight', origin='lower')
    ax1.set_title(f'Vortex Phase Topology (l={l_charge})')
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    fig.colorbar(im1, ax=ax1, label='Phase (rad)')

    # 2. Intensity (Phase Density) Plot
    intensity = amplitude**2
    im2 = ax2.imshow(intensity, extent=[-2, 2, -2, 2], cmap='viridis', origin='lower')
    ax2.set_title('Phase Density (Intensity)')
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    fig.colorbar(im2, ax=ax2, label='Intensity |Psi|^2')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"✓ Vortex visualization saved to: {output_path}")


if __name__ == "__main__":
    generate_vortex_plot(l_charge=1)
