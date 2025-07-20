from __future__ import annotations

from src.talos.tools.example import AlternatingSupervisor, ExampleTool


def test_example_tool_unsupervised() -> None:
    tool = ExampleTool()
    assert tool.run({}) == "Hello, world!"


def test_example_tool_supervised() -> None:
    tool = ExampleTool(supervisor=AlternatingSupervisor())
    assert tool.run({}) == "Blocked by AlternatingSupervisor"
    assert tool.run({}) == "Hello, world!"
    assert tool.run({}) == "Blocked by AlternatingSupervisor"
    assert tool.run({}) == "Hello, world!"
