from talos.geometric_core.skyrmion import LightSkyrmion, translate_topology_to_rna, skyrmion_to_rna_translation, execute_skyrmion_leap

def test_skyrmion_translation():
    skyrmion = LightSkyrmion(charge=1.0)
    codon = translate_topology_to_rna(skyrmion.charge)
    assert codon == "AUG"

    skyrmion_phi = LightSkyrmion(charge=1.618)
    codon_phi = translate_topology_to_rna(skyrmion_phi.charge)
    assert codon_phi == "GCA"

def test_skyrmion_field_translation():
    field = [LightSkyrmion(charge=1.0), LightSkyrmion(charge=3.14)]
    res = skyrmion_to_rna_translation(field)
    assert res["status"] == "RNA nanostructures now encoding CAR-T precision"
    assert "AUG" in res["codons"]
    assert "CGG" in res["codons"]

def test_skyrmion_leap():
    res = execute_skyrmion_leap()
    assert res["event"] == "SKYRMION_BROADCAST_INITIATED"
    assert "8B nodes" in res["reach"]
