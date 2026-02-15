"""
Simulation of the "RJ Lapa Anomaly" scenario.
Demonstrates RFID tracking and protocol application in a theft/recovery event.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta

from talos.arkhe.rfid import RFIDHypergraph, RFIDTag


def run_lapa_scenario() -> None:
    """Runs the Lapa theft and recovery simulation."""
    print("=" * 70)
    print("SCENARIO: RJ LAPA ANOMALY - THEFT & RECOVERY")
    print("=" * 70)

    # Initialize Hypergraph
    h_graph = RFIDHypergraph()

    # Create Tag for a high-value asset
    asset_id = "TAG_RJ_9921"
    asset = RFIDTag(asset_id, "high-value-device", metadata={"owner": "Arquiteto"})
    h_graph.add_tag(asset)

    # 1. Normal State (Geodesic path in Lapa)
    base_time = datetime.now()
    print("\n[STEP 1] Normal tracking in Lapa...")

    # Reading 1: Lapa Arches
    h_graph.register_reading(
        asset_id, "READER_LAPA_01", "Arcos da Lapa", gps=(-22.9133, -43.1806),
        timestamp=base_time
    )

    # Reading 2: Near Selaron
    h_graph.register_reading(
        asset_id, "READER_LAPA_02", "Escadaria Selaron", gps=(-22.9155, -43.1797),
        timestamp=base_time + timedelta(minutes=10)
    )

    # 2. Anomaly Detection (Theft event)
    print("\n[STEP 2] Anomaly detected: Unexpected movement...")
    # Theft happens: move quickly to a distant location
    theft_time = base_time + timedelta(minutes=15)
    h_graph.register_reading(
        asset_id, "READER_SUB_01", "Unknown Zone", gps=(-22.9068, -43.1729),
        timestamp=theft_time
    )

    # Identify anomalies
    anomalies = h_graph.identify_anomalies(threshold=0.8)
    if asset_id in anomalies:
        print(f"  ⚠️ ALERT: Anomaly detected for {asset_id}!")
        print(f"  Current Status: {asset.status}")

    # 3. Protocol Application: FANTASMA
    print("\n[STEP 3] Applying FANTASMA protocol (Surveillance)...")
    h_graph.apply_protocol(asset_id, "FANTASMA")
    print(f"  Tag Status: {asset.status}")

    # 4. Recovery: RESGATE
    print("\n[STEP 4] Location locked. Applying RESGATE protocol...")
    recovery_time = base_time + timedelta(minutes=30)
    h_graph.register_reading(
        asset_id, "READER_POLICE_01", "Recovery Point", gps=(-22.9120, -43.1850),
        timestamp=recovery_time
    )
    h_graph.apply_protocol(asset_id, "RESGATE")
    print(f"  Tag Status: {asset.status}")

    # 5. Final Integration
    print("\n[STEP 5] Asset recovered. Integrating back to Safe Core...")
    h_graph.apply_protocol(asset_id, "INTEGRACAO")
    print(f"  Final Status: {asset.status}")

    # Results
    print("\n" + "-" * 40)
    print(f"Asset Geodesic Path: {' -> '.join(asset.get_path_history())}")
    print(f"Total Handovers: {len(asset.handovers)}")
    print("Scenario Complete. Coherence Restored. ∞")


if __name__ == "__main__":
    run_lapa_scenario()
    time.sleep(0.1)
