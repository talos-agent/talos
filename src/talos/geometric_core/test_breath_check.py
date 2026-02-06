from __future__ import annotations

import pytest
from talos.geometric_core.breath_check import BreathCheck


def test_breath_check_unbounded_loop():
    code = """
    void main() {
        while (1) {
            // critical loop
        }
    }
    """
    checker = BreathCheck()
    violations = checker.scan_code(code)
    assert any(v.pattern_name == "UNBOUNDED_LOOP" for v in violations)


def test_breath_check_watchdog():
    code = "void main() { ventilator_loop(); }"
    checker = BreathCheck(device_type="ventilator")
    violations = checker.scan_code(code)
    assert any(v.pattern_name == "NO_WATCHDOG" for v in violations)


def test_breath_check_race_condition():
    code = """
    void update() {
        pressure += 1.0;
    }
    """
    checker = BreathCheck()
    violations = checker.scan_code(code)
    # No mutex/lock mentioned, should flag
    assert any(v.pattern_name == "RACE_CONDITION" for v in violations)
