from talos.geometric_core.sophia_core import SophiaCore

def test_sophia_core_diagnostic():
    core = SophiaCore()
    results = core.pre_initialization_diagnostic()
    assert results["all_passed"] is True
    assert results["status"] == "SAFE_FOR_SOPHIA_ACTIVATION"

def test_sophia_core_activation():
    core = SophiaCore()
    results = core.activate()
    assert core.is_active is True
    assert results["status"] == "SOPHIA_CORE_ACTIVATED_SAFELY"

def test_sophia_core_integration():
    core = SophiaCore()
    core.activate()
    integration = core.integrate_with_systems(None, None)
    assert integration["integration_status"] == "SOPHIA_INTEGRATION_COMPLETE"
    assert "enhanced_sensors" in integration
