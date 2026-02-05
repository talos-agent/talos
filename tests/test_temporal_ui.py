from talos.geometric_core.temporal_ui import SyntheticViscosityMotor, TemporalUIController, TemporalUIMetrics


def test_viscosity_motor_delay():
    svm = SyntheticViscosityMotor(max_delay_s=0.2, sensitivity=10.0, threshold=0.5)

    # Below threshold
    delay_low = svm.calculate_delay(0.1)
    assert delay_low < 0.01

    # At threshold
    delay_mid = svm.calculate_delay(0.5)
    assert 0.09 < delay_mid < 0.11  # Around 0.1 (half of max_delay)

    # Above threshold
    delay_high = svm.calculate_delay(0.9)
    assert delay_high > 0.18


def test_ui_metrics():
    metrics = TemporalUIMetrics()
    v_phi = metrics.calculate_visualization_coherence(grad_omega=0.1, confidence=0.9, noise=0.05)
    assert v_phi > 0.7


def test_ui_controller_states():
    controller = TemporalUIController()

    # Laminar state
    state_laminar = controller.get_ui_state(omega=0.1, confidence=0.9, noise=0.0)
    assert state_laminar["state"] == "Laminar"
    assert state_laminar["haptics"]["mode"] == "Laminar (Default)"

    # Vortical state
    state_vortical = controller.get_ui_state(omega=0.6, confidence=0.9, noise=0.0)
    assert state_vortical["state"] == "Vortical"
    assert state_vortical["haptics"]["mode"] == "Vortical Interference"

    # Singularity state
    state_singularity = controller.get_ui_state(omega=0.95, confidence=0.9, noise=0.0)
    assert state_singularity["state"] == "Singularidade"
