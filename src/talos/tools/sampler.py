"""A tool for running the sampler CLI."""

from __future__ import annotations

import subprocess
import tempfile

import yaml

from talos.models.sampler import SamplerConfig


def run_sampler(config: SamplerConfig) -> None:
    """Runs the sampler CLI with the given configuration.

    Args:
        config: The sampler configuration.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml") as f:
        yaml.dump(config.model_dump(exclude_none=True), f)
        f.flush()
        subprocess.run(["sampler", "-c", f.name], check=True)