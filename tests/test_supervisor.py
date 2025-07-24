from __future__ import annotations

import asyncio
from langchain_core.tools import tool

from talos.hypervisor.supervisor import Rule, RuleBasedSupervisor, AsyncRuleBasedSupervisor
from talos.tools.supervised_tool import SupervisedTool


def test_rule_based_supervisor():
    """
    Tests that the rule-based supervisor correctly approves or denies actions.
    """

    @tool
    def dummy_tool(x: int) -> int:
        """A dummy tool."""
        return x * 2

    rules = [
        Rule(
            tool_name="dummy_tool",
            validations={"x": lambda x: (x > 0, "x must be greater than 0") if x <= 0 else (True, None)},
        )
    ]
    supervisor = RuleBasedSupervisor(rules=rules)
    supervised_tool = SupervisedTool(
        tool=dummy_tool,
        supervisor=supervisor,
        messages=[],
        name=dummy_tool.name,
        description=dummy_tool.description,
        args_schema=dummy_tool.args_schema,
    )

    # Test that the supervisor approves a valid action.
    assert supervised_tool.run({"x": 1}) == 2

    # Test that the supervisor denies an invalid action.
    result = supervised_tool.run({"x": -1})
    assert result == "x must be greater than 0"


async def test_async_rule_based_supervisor():
    """
    Tests that the async rule-based supervisor correctly approves or denies actions.
    """

    @tool
    def dummy_tool(x: int) -> int:
        """A dummy tool."""
        return x * 2

    rules = [
        Rule(
            tool_name="dummy_tool",
            validations={"x": lambda x: (x > 0, "x must be greater than 0") if x <= 0 else (True, None)},
        )
    ]
    async_supervisor = AsyncRuleBasedSupervisor(rules=rules)
    supervised_tool = SupervisedTool(
        tool=dummy_tool,
        supervisor=None,
        async_supervisor=async_supervisor,
        messages=[],
        name=dummy_tool.name,
        description=dummy_tool.description,
        args_schema=dummy_tool.args_schema,
    )

    # Test that the async supervisor approves a valid action.
    result = await supervised_tool._arun({"x": 1})
    assert result == 2

    # Test that the async supervisor denies an invalid action.
    result = await supervised_tool._arun({"x": -1})
    assert result == "x must be greater than 0"


async def test_async_rule_based_supervisor_direct():
    """
    Tests the async rule-based supervisor directly without the tool wrapper.
    """
    rules = [
        Rule(
            tool_name="test_tool",
            validations={"x": lambda x: (x > 0, "x must be greater than 0") if x <= 0 else (True, None)},
        )
    ]
    async_supervisor = AsyncRuleBasedSupervisor(rules=rules)

    # Test approval
    approved, message = await async_supervisor.approve_async("test_tool", {"x": 1})
    assert approved is True
    assert message is None

    # Test denial
    approved, message = await async_supervisor.approve_async("test_tool", {"x": -1})
    assert approved is False
    assert message == "x must be greater than 0"

    # Test unknown tool
    approved, message = await async_supervisor.approve_async("unknown_tool", {"x": 1})
    assert approved is True
    assert message is None
