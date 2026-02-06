from __future__ import annotations

import pytest
import pandas as pd
from talos.geometric_core.cosmic_synthesizer import SupernovaDataSynthesizer, GalacticASIArchitect


def test_cosmic_synthesizer_match():
    synth = SupernovaDataSynthesizer(
        sn_catalog=pd.DataFrame({'ra': [10.0], 'dec': [20.0], 'type': ['Ia']}),
        snr_catalog=pd.DataFrame({'ra': [10.001], 'dec': [20.001]})
    )
    matches = synth.cross_match(max_sep_deg=0.1)
    assert len(matches) == 1


def test_galactic_asi_predict():
    asi = GalacticASIArchitect()
    z = asi.predict_cgm_enrichment(1e12, 1.0, 0.01)
    assert 0.0 <= z <= 3.0


def test_existential_risk():
    asi = GalacticASIArchitect()
    risk = asi.assess_existential_risk(100) # Very close
    assert risk["threat_level"] == "EXISTENTIAL"
    assert len(risk["recommended_actions"]) > 0
