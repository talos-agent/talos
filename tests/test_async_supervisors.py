from __future__ import annotations

import asyncio
from typing import Any

from pydantic import BaseModel

from talos.tools.base import SupervisedTool, Supervisor, AsyncSupervisor


class SimpleSupervisor(Supervisor[Any]):
    """
    A simple supervisor that approves every other tool call.
    """

    counter: int = 0

    def supervise(self, invocation: Any) -> tuple[bool, str]:
        self.counter += 1
        if self.counter % 2 == 0:
            return True, ""
        return False, "Denied by SimpleSupervisor"


class AsyncSimpleSupervisor(AsyncSupervisor[Any]):
    """
    A simple async supervisor that approves every other tool call.
    """

    counter: int = 0

    async def supervise_async(self, invocation: Any) -> tuple[bool, str]:
        self.counter += 1
        if self.counter % 2 == 0:
            return True, ""
        return False, "Denied by AsyncSimpleSupervisor"


class DummyTool(SupervisedTool):
    """
    A dummy tool for testing.
    """

    name: str = "dummy_tool"
    description: str = "A dummy tool for testing"
    args_schema: type[BaseModel] = BaseModel

    def _run_unsupervised(self, *args: Any, **kwargs: Any) -> Any:
        return "dummy result"

    async def _arun_unsupervised(self, *args: Any, **kwargs: Any) -> Any:
        return "async dummy result"


def test_supervised_tool_supervised() -> None:
    supervisor = SimpleSupervisor()
    supervised_tool = DummyTool()
    supervised_tool.supervisor = supervisor
    
    # First call should be denied
    result = supervised_tool._run({"x": 1})
    assert result == "Denied by SimpleSupervisor"
    
    # Second call should be approved
    result = supervised_tool._run({"x": 1})
    assert result == "dummy result"


def test_supervised_tool_unsupervised() -> None:
    supervised_tool = DummyTool()
    supervised_tool.supervisor = None
    
    result = supervised_tool._run({"x": 1})
    assert result == "dummy result"


async def test_async_supervised_tool_supervised() -> None:
    async_supervisor = AsyncSimpleSupervisor()
    supervised_tool = DummyTool()
    supervised_tool.async_supervisor = async_supervisor
    
    # First call should be denied
    result = await supervised_tool._arun({"x": 1})
    assert result == "Denied by AsyncSimpleSupervisor"
    
    # Second call should be approved
    result = await supervised_tool._arun({"x": 1})
    assert result == "async dummy result"


async def test_async_supervised_tool_unsupervised() -> None:
    supervised_tool = DummyTool()
    supervised_tool.async_supervisor = None
    
    result = await supervised_tool._arun({"x": 1})
    assert result == "async dummy result"


async def test_async_supervised_tool_sync_fallback() -> None:
    """Test that async tools fall back to sync supervisor when no async supervisor is set."""
    supervisor = SimpleSupervisor()
    supervised_tool = DummyTool()
    supervised_tool.supervisor = supervisor
    supervised_tool.async_supervisor = None
    
    # This should use the sync supervisor
    result = await supervised_tool._arun({"x": 1})
    assert result == "Denied by SimpleSupervisor"


def test_async_supervisor_direct() -> None:
    """Test the async supervisor directly."""
    async_supervisor = AsyncSimpleSupervisor()
    
    # Test the first call (should be denied)
    result = asyncio.run(async_supervisor.supervise_async({"test": "data"}))
    assert result == (False, "Denied by AsyncSimpleSupervisor")
    
    # Test the second call (should be approved)
    result = asyncio.run(async_supervisor.supervise_async({"test": "data"}))
    assert result == (True, "") 