from __future__ import annotations

from datetime import datetime, timedelta
from talos.arkhe.rfid import RFIDTag, RFIDHypergraph
import json

def simulate_rj_scenario():
    print("="*70)
    print("ARKHE(n) - RJ LAPA SCENARIO SIMULATION")
    print("="*70)

    hg = RFIDHypergraph()

    # Create the Architect's device node
    device_id = "Γ_DEVICE_RAFAEL_20260215"
    device = RFIDTag(
        tag_id=device_id,
        object_type="Dispositivo_Arquiteto",
        metadata={
            "usuário": "Rafael Oliveira",
            "Ω": "∞",
            "satoshi_inicial": 9.02
        }
    )
    hg.add_tag(device)

    # 1. Normal Geodesic (Copacabana -> Lapa)
    start_time = datetime(2026, 2, 15, 10, 0)

    locations = [
        ("Copacabana", (-22.9691, -43.1868), 0),
        ("Ipanema", (-22.9836, -43.2102), 90),
        ("Lagoa", (-22.9673, -43.2045), 180),
        ("Jardim Botânico", (-22.9686, -43.2263), 300),
        ("Cristo Redentor", (-22.9519, -43.2105), 420),
        ("Lapa", (-22.9133, -43.1806), 540),
    ]

    print("\n🔄 Phase 1: Normal Geodesic Movement")
    for loc_name, coords, minutes in locations:
        timestamp = start_time + timedelta(minutes=minutes)
        hg.register_reading(device_id, f"READER_{loc_name}", loc_name, timestamp, coords)
        print(f"  • {device_id} at {loc_name} (T+{minutes}min)")

    # 2. The Divergence Event (Lapa theft)
    print("\n🚨 Phase 2: Divergence Event (Theft in Lapa)")
    theft_time = start_time + timedelta(minutes=555)
    device.diverge(reason="Stolen/Subtracted in Lapa")

    # Erratic movement towards Santa Teresa
    chaos_path = [
        ("Santa Teresa Ladeira", (-22.9234, -43.1901), 565),
        ("Santa Teresa Interior", (-22.9301, -43.1950), 575),
    ]

    for loc_name, coords, minutes in chaos_path:
        timestamp = start_time + timedelta(minutes=minutes)
        hg.register_reading(device_id, "MESH_CONSENSUS", loc_name, timestamp, coords)
        print(f"  • {device_id} [DIVERGENT] at {loc_name} (T+{minutes}min)")

    # 3. Handle Outcomes
    print("\n⚖️ Phase 3: Handling Protocols")

    # Show status before choice
    print(f"  Current Node Status: {device.status}")
    print(f"  System Coherence: {hg.compute_system_coherence():.4f}")

    print("\n  Executing Protocol FANTASMA (Observe)...")
    result = hg.protocol_fantasma(device_id)
    print(f"  Result: {result}")

    # Final Telemetry
    print("\n📊 Final Telemetry (Summary):")
    print(json.dumps(json.loads(device.to_json()), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    simulate_rj_scenario()
