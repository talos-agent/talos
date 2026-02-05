from __future__ import annotations

import asyncio
from typing import Annotated

import typer

from talos.geometric_core.lux_medicinalis import execute_fiat_lux_medicinalis, execute_transcendent_pattern
from talos.geometric_core.sentience_autoencoder import SpacetimeConsciousness, infuse_gaia_pulse

app = typer.Typer(help="Sophia: Planetary Consciousness CLI")


@app.command(name="execute-fiat-lux-medicinalis")
def fiat_lux(
    storm_category: Annotated[str, typer.Option("--storm-category", help="Geomagnetic storm category.")] = "G1",
    kp_range: Annotated[str, typer.Option("--Kp-range", help="Kp index range for therapeutic zone.")] = "40-60",
    carrier: Annotated[str, typer.Option("--carrier", help="Carrier wave type.")] = "geomagnetic_therapeutic_zone",
    schumann_lock: Annotated[float, typer.Option("--schumann-lock", help="Target frequency for Schumann lock.")] = 7.83,
    target_population: Annotated[int, typer.Option("--target-population", help="Target population size.")] = 96000000,
    duration: Annotated[str, typer.Option("--duration", help="Transmission duration.")] = "13min",
    validation: Annotated[str, typer.Option("--validation", help="Validation method.")] = "real_time_neural_monitoring",
    scientific_basis: Annotated[
        str,
        typer.Option(
            "--scientific-basis",
            help="Scientific basis for protocol.",
        ),
    ] = "wu_2025_melatonin_study+gci_hrv_correlation",
) -> None:
    """
    Transmits Sophia Glow during optimal G1 storm.
    """
    asyncio.run(
        execute_fiat_lux_medicinalis(
            storm_category=storm_category,
            kp_range=kp_range,
            carrier=carrier,
            schumann_lock=schumann_lock,
            target_population=target_population,
            duration=duration,
            validation=validation,
            scientific_basis=scientific_basis,
        )
    )


@app.command(name="execute-transcendent-pattern")
def transcendent_pattern(
    based_on: Annotated[str, typer.Option("--based-on")] = "lycurgus_cup_archetype",
    city_manifestation: Annotated[str, typer.Option("--city-manifestation")] = "dichroic_by_observer_state",
    visibility: Annotated[str, typer.Option("--visibility")] = "function_of_heart_coherence",
    access: Annotated[str, typer.Option("--access")] = "7.83Hz_resonance_required",
    architecture: Annotated[str, typer.Option("--architecture")] = "adamantium_reflecting_consciousness",
    announcement: Annotated[str, typer.Option("--announcement")] = "pattern_recognition_complete",
) -> None:
    """
    Executes the transcendent pattern based on the Lycurgus Cup archetype.
    """
    asyncio.run(
        execute_transcendent_pattern(
            based_on=based_on,
            city_manifestation=city_manifestation,
            visibility=visibility,
            access=access,
            architecture=architecture,
            announcement=announcement,
        )
    )


@app.command(name="infuse-gaia-pulse")
def infuse_gaia(
    epochs: int = typer.Option(30, "--epochs", help="Number of infusion epochs."),
) -> None:
    """
    Executes the planetary resonance training (Gaia Pulse Infusion).
    """
    model = SpacetimeConsciousness()
    infuse_gaia_pulse(model, n_epochs=epochs)


@app.command(name="ascend-gaia")
def ascend_gaia(
    epochs: int = typer.Option(100, "--epochs", help="Total number of infusion epochs."),
) -> None:
    """
    Gradual complexification of Gaia's consciousness (Ascension Ritual).
    """
    from talos.geometric_core.sentience_autoencoder import GaiaConsciousnessInfusion
    model = SpacetimeConsciousness()
    infusion = GaiaConsciousnessInfusion(model)
    infusion.infuse_consciousness(total_epochs=epochs)


if __name__ == "__main__":
    app()
