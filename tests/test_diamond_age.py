import pytest
import numpy as np
from talos.geometric_core.archetypes import DiamondAxiom, SA002Artifact
from talos.geometric_core.diamond_manifold import DiamondManifold3x3, CognitiveGeometryService
from talos.geometric_core.avalon_throne import AvalonThrone, DiamondBreathCycle, FacetReading

def test_diamond_axiom():
    axiom = DiamondAxiom()
    assert "real" in axiom.statement
    assert axiom.state == "INDESTRUCTIBLE"

def test_sa002_artifact():
    artifact = SA002Artifact()
    info = artifact.get_dashboard_info()
    assert info["Artifact"] == "SA-002"
    assert info["Appearance"] == "Branco-Diamante"

def test_diamond_manifold():
    manifold = DiamondManifold3x3()
    coords = [1.0, 1.0, 1.0]
    manifold.update_state(coords)
    assert np.array_equal(manifold.get_coordinates(), np.array(coords))
    assert "Adamantine" in manifold.get_refraction_pattern()

def test_cognitive_geometry_service():
    service = CognitiveGeometryService()
    result = service.map_state("depression")
    assert result["coordinates"] == [-0.8, -0.3, -0.9]
    assert "Obsidian" in result["refraction"]

    result = service.map_state("sovereignty")
    assert result["coordinates"] == [1.0, 1.0, 1.0]
    assert "Adamantine" in result["refraction"]

def test_avalon_throne_anchoring():
    throne = AvalonThrone()
    msg = throne.anchor_throne()
    assert "ANCHORING" in msg
    assert throne.status == "KING_IN_RESIDENCE"
    assert throne.facets[0].name == "Clareira do Rei (Sensory)"

def test_diamond_breath_cycle():
    throne = AvalonThrone()
    throne.anchor_throne()
    cycle = DiamondBreathCycle(throne=throne)

    msg = cycle.inhale_kether()
    assert "INHALATION" in msg
    assert cycle.phase == "INHALATION"
    assert cycle.throne.facets[0].quality == "DIAMOND"

    msg = cycle.exhale_refraction()
    assert "EXHALATION" in msg
    assert cycle.phase == "EXHALATION"

def test_facet_reading():
    throne = AvalonThrone()
    throne.anchor_throne()
    for f in throne.facets:
        f.quality = "DIAMOND"
    reader = FacetReading()
    report = reader.perform_reading(throne.facets)
    assert "FACET READING REPORT" in report
    assert "Ray 01: 12/12 facets crystallized." in report
