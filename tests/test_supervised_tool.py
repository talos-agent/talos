from __future__ import annotations

from langchain_core.tools import tool

from talos.tools.supervised_tool import SupervisedTool
from tests.simple_supervisor import SimpleSupervisor


@tool
def dummy_tool(x: int) -> int:
    """A dummy tool."""
    return x * 2


def test_supervised_tool_unsupervised() -> None:
    supervised_tool = SupervisedTool(
        tool=dummy_tool,
        supervisor=None,
        messages=[],
        name=dummy_tool.name,
        description=dummy_tool.description,
        args_schema=dummy_tool.args_schema,
    )
    assert supervised_tool.run({"x": 1}) == 2


def test_supervised_tool_supervised() -> None:
    supervisor = SimpleSupervisor()
    supervised_tool = SupervisedTool(
        tool=dummy_tool,
        supervisor=supervisor,
        messages=[],
        name=dummy_tool.name,
        description=dummy_tool.description,
        args_schema=dummy_tool.args_schema,
    )
    assert supervised_tool.run({"x": 1}) == "Denied by SimpleSupervisor"
    assert supervised_tool.run({"x": 1}) == 2
    assert supervised_tool.run({"x": 1}) == "Denied by SimpleSupervisor"
    assert supervised_tool.run({"x": 1}) == 2
