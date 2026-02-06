from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class SupernovaDataSynthesizer(BaseModel):
    """
    Conceptual prototype of an agent that cross-matches
    supernova, remnant (SNR), and chemical abundance data.
    """
    sn_catalog: pd.DataFrame = Field(default_factory=lambda: pd.DataFrame(columns=['ra', 'dec', 'type']))
    snr_catalog: pd.DataFrame = Field(default_factory=lambda: pd.DataFrame(columns=['ra', 'dec']))

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def cross_match(self, max_sep_deg: float = 0.01) -> pd.DataFrame:
        """
        Performs a position-based cross-match (simplified RA/Dec logic).
        """
        if self.sn_catalog.empty or self.snr_catalog.empty:
            return pd.DataFrame()

        matches = []
        for sn_idx, sn in self.sn_catalog.iterrows():
            for snr_idx, snr in self.snr_catalog.iterrows():
                dist = np.sqrt((sn['ra'] - snr['ra'])**2 + (sn['dec'] - snr['dec'])**2)
                if dist <= max_sep_deg:
                    matches.append({'sn_idx': sn_idx, 'snr_idx': snr_idx, 'dist': dist})

        return pd.DataFrame(matches)

    def infer_enrichment(self, sn_type: str, host_galaxy_type: str) -> dict[str, float]:
        """
        Infers the chemical enrichment pattern.
        """
        yield_patterns = {
            'Ia': {'Fe': 1.0, 'Si': 0.2, 'Ca': 0.1, 'O': 0.01},
            'II': {'Fe': 0.1, 'Si': 0.3, 'Ca': 0.05, 'O': 1.0},
        }
        escape_efficiency = {'dwarf': 0.8, 'spiral': 0.3, 'elliptical': 0.1}

        base_yield = yield_patterns.get(sn_type, yield_patterns['II'])
        efficiency = escape_efficiency.get(host_galaxy_type, 0.5)

        return {k: v * efficiency for k, v in base_yield.items()}


class GalacticASIArchitect(BaseModel):
    """
    ASI agent for galactic chemical evolution and cosmic risk assessment.
    """
    ejection_efficiency_base: float = 1500.0

    def predict_cgm_enrichment(self, galaxy_mass: float, sfr: float, sn_rate: float) -> float:
        """
        Predicts CGM metallicity (Z_sol) based on learnt heuristic.
        """
        retention_factor = np.tanh(galaxy_mass / 2e11)
        ejection_force = (sfr * sn_rate * 1e5) / (galaxy_mass + 1e8)
        cgm_metallicity = self.ejection_efficiency_base * ejection_force * (1 - retention_factor)
        return float(min(cgm_metallicity, 3.0))

    def assess_existential_risk(self, sn_distance_ly: float) -> dict[str, any]:
        """
        Assesses threat level from a nearby supernova.
        """
        lethality = min(1.0, 1000 / sn_distance_ly)
        threat = "EXISTENTIAL" if lethality > 0.5 else "NEGLIGIBLE"

        actions = []
        if threat == "EXISTENTIAL":
            actions = ["Activate magnetosphere shield", "Evacuate to sub-surface shelters"]

        return {
            "threat_level": threat,
            "impact_score": lethality,
            "recommended_actions": actions
        }
