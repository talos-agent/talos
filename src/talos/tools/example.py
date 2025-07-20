from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from .base import Supervisor, SupervisedTool


class AlternatingSupervisor(Supervisor[Any]):
    """
    A supervisor that alternates between allowing and denying tool invocations.
    """

    def __init__(self) -> None:
        self.counter = 0

    def supervise(self, invocation: Any) -> tuple[bool, str]:
        if self.counter % 2 == 0:
            self.counter += 1
            return False, "Blocked by AlternatingSupervisor"
        self.counter += 1
        return True, ""


class ExampleTool(SupervisedTool):
    """
    An example tool that can be supervised.
    """

    name: str = "example_tool"
    description: str = "An example tool that can be supervised"
    args_schema: type[BaseModel] = BaseModel

    def _run_unsupervised(self, *args: Any, **kwargs: Any) -> Any:
        return "Hello, world!"
