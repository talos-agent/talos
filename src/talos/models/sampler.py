"""Pydantic models for sampler."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RunchartItem(BaseModel):
    """A single item in a runchart."""

    label: str
    sample: str
    color: int | None = None


class RunchartLegend(BaseModel):
    """The legend for a runchart."""

    enabled: bool = True
    details: bool = True


class TriggerActions(BaseModel):
    """Actions for a trigger."""

    terminal_bell: bool = False
    sound: bool = False
    visual: bool = False
    script: str | None = None


class Trigger(BaseModel):
    """A trigger component."""

    title: str
    condition: str
    actions: TriggerActions


class InteractiveShell(BaseModel):
    """Interactive shell support."""

    pty: bool = False
    init: str | None = None
    transform: str | None = None
    multistep_init: list[str] | None = None


class Component(BaseModel):
    """Base model for a component."""

    title: str
    rate_ms: int = 1000
    triggers: list[Trigger] | None = None
    position: list[list[int]] | None = None
    interactive_shell: InteractiveShell | None = None


class Runchart(Component):
    """A runchart component."""

    scale: int = 1
    legend: RunchartLegend = Field(default_factory=RunchartLegend)
    items: list[RunchartItem]


class Sparkline(Component):
    """A sparkline component."""

    scale: int = 0
    sample: str


class BarchartItem(BaseModel):
    """A single item in a barchart."""

    label: str
    sample: str
    color: int | None = None


class Barchart(Component):
    """A barchart component."""

    scale: int = 0
    items: list[BarchartItem]


class GaugeValue(BaseModel):
    """A value for a gauge."""

    sample: str


class Gauge(Component):
    """A gauge component."""

    scale: int = 2
    percent_only: bool = False
    color: int | None = None
    cur: GaugeValue
    max: GaugeValue
    min: GaugeValue


class Textbox(Component):
    """A textbox component."""

    sample: str
    border: bool = True
    color: int | None = None


class Asciibox(Component):
    """An asciibox component."""

    font: str = "3d"
    border: bool = False
    color: int | None = None
    sample: str
    size: list[int] | None = None


class SamplerConfig(BaseModel):
    """The root model for the sampler configuration."""

    variables: dict[str, str] | None = None
    theme: str | None = None
    runcharts: list[Runchart] | None = None
    sparklines: list[Sparkline] | None = None
    barcharts: list[Barchart] | None = None
    gauges: list[Gauge] | None = None
    textboxes: list[Textbox] | None = None
    asciiboxes: list[Asciibox] | None = None