from __future__ import annotations

import time
from pydantic import BaseModel, ConfigDict, Field
from talos.geometric_core.vitality import UrbanPulse, CitySensor, NoiseSensor, TrafficSensor
from talos.geometric_core.gardener import DigitalGardener


class TiferetDashboard(BaseModel):
    """
    Orchestrates the Listen -> Diagnose -> Cure cycle (The Dashboard of Harmony).
    """
    pulse: UrbanPulse
    gardener: DigitalGardener = Field(default_factory=DigitalGardener)
    cycle_count: int = 0

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def run_cycle(self) -> dict[str, any]:
        """
        Executes one full cycle of urban harmony monitoring and healing.
        """
        self.cycle_count += 1
        results = {
            "cycle": self.cycle_count,
            "timestamp": time.time(),
            "city": self.pulse.city_name,
            "issues": [],
            "cures": []
        }

        # 1. LISTEN & DIAGNOSE
        # Simulate diagnostics based on vitality logic
        vitality = self.pulse.compute_vitality()

        # Identify specific issues (mocking logic for simplicity)
        issues = []
        for sensor in self.pulse.sensors:
            val = sensor.read()
            print(f"DEBUG: Sensor {sensor.name} read {val} (type: {type(sensor)}) mock: {sensor.mock_mode}")
            if isinstance(sensor, NoiseSensor) and val > 75:
                issues.append("ESTRESSE ACÚSTICO")
            if isinstance(sensor, TrafficSensor) and val > 0.7:
                issues.append("AR TÓXICO") # High traffic implies bad air in this simple model

        results["issues"] = issues
        results["vitality"] = vitality

        # 2. CURE (The Gardener)
        if issues:
            cures = self.gardener.prescribe_cure(issues)
            results["cures"] = cures
        else:
            results["cures"] = ["Homeostase alcançada. Nenhuma ação necessária."]

        return results

    def display_report(self, results: dict[str, any]):
        print(f"\n{'='*15} CICLO VITAL TIFERET #{results['cycle']:04d} {'='*15}")
        print(f"📍 Cidade: {results['city']}")
        print(f"📊 Vitalidade: {results['vitality']:.2f}")

        if results["issues"]:
            print(f"⚠️  ALERTAS: {', '.join(results['issues'])}")
            print("\n>>> PROTOCOLOS DE CURA SUGERIDOS <<<")
            for cure in results["cures"]:
                print(f"   {cure}")
        else:
            print("✅ STATUS: A cidade está em harmonia.")
        print(f"{'='*50}\n")
