from __future__ import annotations

import asyncio
from langchain_core.tools import tool

from talos.tools.supervised_tool import SupervisedTool
from tests.simple_supervisor import SimpleSupervisor, AsyncSimpleSupervisor


@tool
def dummy_tool(x: int) -> int:
    """A dummy tool."""
    return x * 2


async def dummy_async_tool(x: int) -> int:
    """A dummy async tool."""
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


async def test_async_supervised_tool_unsupervised() -> None:
    supervised_tool = SupervisedTool(
        tool=dummy_tool,
        supervisor=None,
        async_supervisor=None,
        messages=[],
        name=dummy_tool.name,
        description=dummy_tool.description,
        args_schema=dummy_tool.args_schema,
    )
    result = await supervised_tool._arun({"x": 1})
    assert result == 2


async def test_async_supervised_tool_with_async_supervisor() -> None:
    async_supervisor = AsyncSimpleSupervisor()
    supervised_tool = SupervisedTool(
        tool=dummy_tool,
        supervisor=None,
        async_supervisor=async_supervisor,
        messages=[],
        name=dummy_tool.name,
        description=dummy_tool.description,
        args_schema=dummy_tool.args_schema,
    )
    
    # First call should be denied
    result = await supervised_tool._arun({"x": 1})
    assert result == "Denied by AsyncSimpleSupervisor"
    
    # Second call should be approved
    result = await supervised_tool._arun({"x": 1})
    assert result == 2


async def test_async_supervised_tool_sync_fallback() -> None:
    """Test that async tools fall back to sync supervisor when no async supervisor is set."""
    supervisor = SimpleSupervisor()
    supervised_tool = SupervisedTool(
        tool=dummy_tool,
        supervisor=supervisor,
        async_supervisor=None,
        messages=[],
        name=dummy_tool.name,
        description=dummy_tool.description,
        args_schema=dummy_tool.args_schema,
    )
    
    # This should use the sync supervisor
    result = await supervised_tool._arun({"x": 1})
    assert result == "Denied by SimpleSupervisor"


def test_supervised_tool_set_async_supervisor() -> None:
    """Test setting async supervisor on supervised tool."""
    supervised_tool = SupervisedTool(
        tool=dummy_tool,
        supervisor=None,
        messages=[],
        name=dummy_tool.name,
        description=dummy_tool.description,
        args_schema=dummy_tool.args_schema,
    )
    
    async_supervisor = AsyncSimpleSupervisor()
    supervised_tool.set_async_supervisor(async_supervisor)
    
    assert supervised_tool.async_supervisor is not None
    assert supervised_tool.async_supervisor == async_supervisor
