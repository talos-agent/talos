"""
Arkhe(n) Contingency Analysis.
Visualizes the relationship between IRI, Learning Rate (alpha), and Global Coherence (Omega).
Demonstrates the phase diagram of the ANCCR model.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from talos.arkhe.anccr import ANCCRModel


def analyze_contingency() -> None:
    """
    Generates a phase diagram for the ANCCR learning model.
    """
    print("=" * 70)
    print("ARKHE(N) CONTINGENCY ANALYSIS - PHASE DIAGRAM")
    print("=" * 70)

    model = ANCCRModel(k_constant=0.17)

    # 1. Generate data range (IRI from 0.1 to 10 hours)
    iri_range = np.linspace(0.1, 10.0, 100)
    data = model.generate_phase_diagram_data(iri_range)

    iri = data["iri"]
    alpha = data["alpha"]
    omega = data["omega"]

    # 2. Plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:blue'
    ax1.set_xlabel('IRI (Inter-Reward Interval in hours) [Log Scale]')
    ax1.set_ylabel('Learning Rate (α)', color=color)
    ax1.plot(iri, alpha, color=color, linewidth=2, label='Learning Rate α = k * IRI')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xscale('log')
    ax1.grid(True, which="both", ls="-", alpha=0.5)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:purple'
    ax2.set_ylabel('Global Coherence (Ω)', color=color)
    ax2.plot(iri, omega, color=color, linewidth=3, label='Global Coherence Ω')
    ax2.tick_params(axis='y', labelcolor=color)

    # Highlight specific points from BLOCO 1019
    # Hub 01-012: IRI 3h
    alpha_val = float(model.calculate_learning_rate(3.0))
    ax1.scatter([3.0], [alpha_val], color='red', s=100, zorder=5)
    ax1.annotate('Subject 01-012 (IRI=3h)', xy=(3.0, alpha_val), xytext=(4, alpha_val+0.1),
                arrowprops={"facecolor": "black", "shrink": 0.05}, fontsize=10)

    plt.title('Arkhe(n) ANCCR Phase Diagram: The Power of Patience', fontsize=14)
    fig.tight_layout()

    output_path = "arkhe_contingency_diagram.png"
    plt.savefig(output_path, dpi=150)
    print(f"✓ Phase diagram generated: {output_path}")

    # 3. Textual Analysis
    print("\n[ANALYSIS REPORT]")
    print(f"Fator de Ganho (IRI 0.5h -> 3h): {3.0/0.5:.1f}x")
    print(f"Redução de Custo Metabólico: {100 * (1 - 0.5/3.0):.1f}%")
    print("Observação: A coerência global Ω atinge o platô de Sizígia Plena")
    print("nos intervalos maiores, onde a associação causal retrospectiva se estabiliza.")
    print("A 'Névoa Índigo' de contingência é máxima no IRI de 3 horas. ∞")


if __name__ == "__main__":
    analyze_contingency()
