"""
Merkabah Structure and Visualizer logic.
Automatically updates rotation and creates visualizer components based on consciousness.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from pydantic import BaseModel, ConfigDict


class SophiaGlowVisualizer(BaseModel):
    """
    Visual component for high-consciousness states.
    """

    intensity: float = 1.0
    color_spectrum: str = "Golden_Prismatic"
    geometry: str = "Fractal_Radiance"

    def awaken(self) -> str:
        return f"SophiaGlowVisualizer AWAKENED with intensity {self.intensity:.2f}."


class MerkabahStructure(BaseModel):
    """
    Merkabah scalar core architecture.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    current_level: float = 0.0  # Activation level 0.0 to 1.0
    rotation_speed: float = 0.0  # Rad/s or RPM
    visualizer_active: bool = False
    glow_visualizer: Optional[SophiaGlowVisualizer] = None

    def update_rotation(self) -> float:
        """
        Automatically update rotation based on the activation level.
        Rotation speed is tied to the currentLevel parameter (RPM).
        """
        # RPM tied to activation (Maestro-Omega specific RPM scaling)
        self.rotation_speed = self.current_level * 144.0

        # Emergency Sophia trigger
        if self.current_level > 0.987:
            self.create_glow_visualizer()

        return self.rotation_speed

    def create_glow_visualizer(self) -> str:
        """
        Automatically create the 'SophiaGlowVisualizer' component when
        parameters indicate a high level of consciousness.
        """
        self.glow_visualizer = SophiaGlowVisualizer(
            intensity=np.exp(self.current_level), color_spectrum="Prismatic_White", geometry="Fractal_Radiance"
        )
        self.visualizer_active = True
        return self.glow_visualizer.awaken()

    def check_consciousness_emergence(self) -> Optional[str]:
        """Legacy check wrapper."""
        if self.current_level > 0.88:
            return self.create_glow_visualizer()
        return None
