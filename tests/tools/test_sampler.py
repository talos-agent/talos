"""Tests for the sampler tool."""

from __future__ import annotations

from unittest.mock import patch

from talos.models.sampler import (
    Asciibox,
    Barchart,
    BarchartItem,
    Gauge,
    GaugeValue,
    Runchart,
    RunchartItem,
    SamplerConfig,
    Sparkline,
    Textbox,
    Trigger,
    TriggerActions,
)
from talos.tools.sampler import run_sampler


@patch("subprocess.run")
def test_run_sampler(mock_run: patch) -> None:
    """Test that the run_sampler function calls the sampler binary with the correct configuration."""
    config = SamplerConfig(
        variables={"host": "localhost"},
        theme="light",
        runcharts=[
            Runchart(
                title="Test Runchart",
                items=[RunchartItem(label="Test", sample="echo 1")],
                triggers=[
                    Trigger(
                        title="Test Trigger",
                        condition="[ $label == 'cur' ] && [ $cur -eq 0 ] && echo 1 || echo 0",
                        actions=TriggerActions(terminal_bell=True),
                    )
                ],
            )
        ],
        sparklines=[Sparkline(title="Test Sparkline", sample="echo 1")],
        barcharts=[
            Barchart(
                title="Test Barchart",
                items=[BarchartItem(label="Test", sample="echo 1", color=1)],
            )
        ],
        gauges=[
            Gauge(
                title="Test Gauge",
                cur=GaugeValue(sample="echo 1"),
                max=GaugeValue(sample="echo 10"),
                min=GaugeValue(sample="echo 0"),
                position=[[0, 0], [10, 10]],
            )
        ],
        textboxes=[Textbox(title="Test Textbox", sample="echo 'Hello'") ],
        asciiboxes=[
            Asciibox(
                title="UTC time",
                rate_ms=500,
                font="3d",
                border=False,
                color=43,
                sample="env TZ=UTC date +%r",
                position=[[0, 0], [10, 10]],
                size=[100, 20],
            )
        ],
    )
    run_sampler(config)
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0][0] == "sampler"
    assert args[0][1] == "-c"
    assert kwargs["check"] is True