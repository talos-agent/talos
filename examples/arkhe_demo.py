"""
Demonstration script for Arkhe(n) framework.
Showcases UCD, RFID, Arkhen(11), and Swimmer modules.
"""

from datetime import datetime, timedelta
import numpy as np

from talos.arkhe.ucd import UCD
from talos.arkhe.rfid import RFIDTag, RFIDHypergraph
from talos.arkhe.arkhen_11 import Arkhen11
from talos.arkhe.swimmer import FlagellarSwimmer
from talos.arkhe.visualization import PolyglotUCDNetwork


def demo_ucd():
    """Demonstrates Universal Coherence Detection."""
    print("--- UCD Demo ---")
    data = np.random.rand(10, 5)
    ucd = UCD(data)
    analysis = ucd.analyze()
    print(f"Coherence C: {analysis['C']:.4f}, Fluctuation F: {analysis['F']:.4f}")
    print(f"Conservation verified: {analysis['conservation']}")


def demo_rfid():
    """Demonstrates RFID tracking in a hypergraph."""
    print("\n--- RFID Demo ---")
    hg = RFIDHypergraph()
    tag = RFIDTag("TAG_ALPHA", "Asset")
    hg.add_tag(tag)

    now = datetime.now()
    hg.register_reading("TAG_ALPHA", "READER_1", "Warehouse A", timestamp=now)
    hg.register_reading("TAG_ALPHA", "READER_2", "Transit", timestamp=now + timedelta(hours=1))
    hg.register_reading("TAG_ALPHA", "READER_3", "Warehouse B", timestamp=now + timedelta(hours=2))

    print(f"Tag Path: {' -> '.join(tag.get_path_history())}")
    print(f"Effective Dimension: {tag.get_effective_dimension():.2f}")


def demo_arkhen():
    """Demonstrates Arkhen(11) hypergraph."""
    print("\n--- Arkhen(11) Demo ---")
    a11 = Arkhen11()
    print(f"System Coherence: {a11.compute_coherence():.4f}")
    print("Generating visualization (arkhen_11_demo.png)...")
    a11.visualize("arkhen_11_demo.png")


def demo_swimmer():
    """Demonstrates Flagellar Swimmer simulation."""
    print("\n--- Swimmer Demo ---")
    swimmer = FlagellarSwimmer(length=5.0, dt=0.05)
    print("Simulating swimmer...")
    hx, hy, _ = swimmer.run(t_max=1.0)
    print(f"Final position: ({hx[-1]:.4f}, {hy[-1]:.4f})")


def demo_visualization():
    """Demonstrates Polyglot UCD Network visualization."""
    print("\n--- Polyglot Visualization Demo ---")
    poly = PolyglotUCDNetwork()
    print("Generating polyglot hypergraph (polyglot_demo.png)...")
    poly.visualize("polyglot_demo.png")


if __name__ == "__main__":
    demo_ucd()
    demo_rfid()
    demo_arkhen()
    demo_swimmer()
    demo_visualization()
    print("\nDemo complete. ∞")
