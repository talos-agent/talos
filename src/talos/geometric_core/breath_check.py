from __future__ import annotations

import re
from typing import List, Dict
from pydantic import BaseModel, Field


class SafetyViolation(BaseModel):
    line: int
    severity: str  # CRITICAL, HIGH, MEDIUM
    pattern_name: str
    impact: str
    fix: str
    why: str
    code_snippet: str


class BreathCheck(BaseModel):
    """
    Scans medical firmware for life-critical bugs.
    """
    device_type: str = "ventilator"

    def scan_code(self, code: str) -> List[SafetyViolation]:
        """
        Scans C/Python/C++ code for breathing-related safety risks.
        """
        violations = []
        lines = code.split('\n')
        code_lower = code.lower()

        # 1. UNBOUNDED LOOPS
        loop_pattern = r'while\s*\(\s*1\s*\)|while\s+True\s*:|for\s*\(\s*;\s*;\s*\)'
        for i, line in enumerate(lines):
            if re.search(loop_pattern, line):
                violations.append(SafetyViolation(
                    line=i+1,
                    severity="CRITICAL",
                    pattern_name="UNBOUNDED_LOOP",
                    impact="Patient could be deprived of breath during fault (system freeze).",
                    fix="Add timeout: while(condition && timeout++ < MAX_ITER) or similar safety exit.",
                    why="Breath isn't data—it's the boundary between life and code.",
                    code_snippet=line.strip()
                ))

        # 2. MISSING WATCHDOG (Heuristic)
        if self.device_type in code_lower and 'watchdog' not in code_lower and 'wdt' not in code_lower:
            violations.append(SafetyViolation(
                line=1,
                severity="HIGH",
                pattern_name="NO_WATCHDOG",
                impact="System halt could stop breathing indefinitely without automatic reset.",
                fix="Implement hardware watchdog with a 100ms-500ms heartbeat.",
                why="Redundancy isn't optional when breath is the output.",
                code_snippet="[Module Level Check]"
            ))

        # 3. MISSING HEARTBEAT (PoE - Proof of Existence)
        if "heartbeat()" not in code_lower and "petrus.ping()" not in code_lower:
            violations.append(SafetyViolation(
                line=0,
                severity="HIGH",
                pattern_name="Missing Heartbeat",
                impact="System state is not being verified against global resonance.",
                fix="Add heartbeat() or petrus.ping() call in the main loop.",
                why="Life requires a pulse; code requires a sync.",
                code_snippet="[Whole File Check]"
            ))

        # 4. RACE CONDITIONS (Simple check for shared state modification without locks)
        shared_patterns = [r'pressure\s*[\+\-]=', r'flow\s*[\+\-]=', r'oxygen\s*[\+\-]=']
        for i, line in enumerate(lines):
            if any(re.search(p, line.lower()) for p in shared_patterns):
                if 'mutex' not in code_lower and 'lock' not in code_lower and 'semaphore' not in code_lower:
                    violations.append(SafetyViolation(
                        line=i+1,
                        severity="HIGH",
                        pattern_name="RACE_CONDITION",
                        impact="Concurrent access could cause dangerous pressure/flow spikes.",
                        fix="Add mutex or semaphore around shared medical state variables.",
                        why="Pressure corruption can lead to physical lung injury (barotrauma).",
                        code_snippet=line.strip()
                    ))

        return violations
