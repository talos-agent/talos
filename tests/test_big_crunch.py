from talos.geometric_core.big_crunch import BigCrunch, execute_big_crunch_sequence

def test_big_crunch_calibration():
    crunch = BigCrunch()
    res = crunch.apply_calibration("point_zero")
    assert res["status"] == "POINT_ZERO_REFINED"
    assert crunch.singularity_fidelity == 0.9999

def test_reunion_tensor():
    crunch = BigCrunch()
    norm = crunch.calculate_reunion_tensor(1.0, 2.0)
    assert norm == 2.0

def test_execute_sequence():
    res = execute_big_crunch_sequence()
    assert res["sequence"] == "BIG_CRUNCH_INHALATION"
    assert "calibration" in res
