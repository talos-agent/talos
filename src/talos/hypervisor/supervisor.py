from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Tuple

from pydantic import BaseModel, Field


class Rule(BaseModel):
    """
    A rule for a supervisor to follow.
    """

    tool_name: str
    # A function that takes the tool arguments and returns whether the action is
    # approved.
    # The `Any` is the value of the argument.
    # The `bool` is whether the action is approved.
    # The `Callable` is the function that takes the value and returns the bool.
    # The `dict` is the dictionary of arguments.
    # So the whole type hint is a dictionary of argument names to functions that
    # approve or deny the action.
    validations: dict[str, Callable[[Any], Tuple[bool, Optional[str]]]] = Field(default_factory=dict)


class Supervisor(BaseModel, ABC):
    """
    An abstract base class for supervisors.
    """

    @abstractmethod
    def approve(self, action: str, args: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Approves or denies an action.
        """
        pass


class AsyncSupervisor(BaseModel, ABC):
    """
    An abstract base class for async supervisors.
    """

    @abstractmethod
    async def approve_async(self, action: str, args: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Approves or denies an action asynchronously.
        """
        pass


class RuleBasedSupervisor(Supervisor):
    """
    A supervisor that uses a set of rules to approve or deny actions.
    """

    rules: list[Rule]

    def approve(self, action: str, args: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Approves or denies an action based on the rules.
        """
        for rule in self.rules:
            if rule.tool_name == action:
                for arg_name, validation_fn in rule.validations.items():
                    if arg_name in args:
                        approved, error_message = validation_fn(args[arg_name])
                        if not approved:
                            return False, error_message
        return True, None


class AsyncRuleBasedSupervisor(AsyncSupervisor):
    """
    An async supervisor that uses a set of rules to approve or deny actions.
    """

    rules: list[Rule]

    async def approve_async(self, action: str, args: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Approves or denies an action based on the rules asynchronously.
        """
        for rule in self.rules:
            if rule.tool_name == action:
                for arg_name, validation_fn in rule.validations.items():
                    if arg_name in args:
                        approved, error_message = validation_fn(args[arg_name])
                        if not approved:
                            return False, error_message
        return True, None


class SimpleSupervisor(Supervisor):
    """
    A simple supervisor that approves every other tool call.
    """

    counter: int = 0

    def approve(self, action: str, args: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Approves or denies an action.
        """
        self.counter += 1
        if self.counter % 2 == 0:
            return True, None
        return False, "Denied by SimpleSupervisor"


class AsyncSimpleSupervisor(AsyncSupervisor):
    """
    A simple async supervisor that approves every other tool call.
    """

    counter: int = 0

    async def approve_async(self, action: str, args: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Approves or denies an action asynchronously.
        """
        self.counter += 1
        if self.counter % 2 == 0:
            return True, None
        return False, "Denied by AsyncSimpleSupervisor"
