from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from langchain.tools import BaseTool
from pydantic import Field

T = TypeVar("T")


class Supervisor(ABC, Generic[T]):
    """
    A supervisor can be used to analyze a tool invocation and determine if it is
    malicious or not. If it is malicious, the supervisor can short-circuit the
    tool execution and provide an error message.
    """

    @abstractmethod
    def supervise(self, invocation: T) -> tuple[bool, str]:
        """
        Analyze the tool invocation and determine if it is malicious or not.

        Args:
            invocation: The tool invocation to analyze.

        Returns:
            A tuple of a boolean and a string. If the invocation is malicious,
            the boolean is False and the string is an error message. Otherwise,
            the boolean is True and the string is empty.
        """
        raise NotImplementedError


class AsyncSupervisor(ABC, Generic[T]):
    """
    An async supervisor can be used to analyze a tool invocation and determine if it is
    malicious or not. This is the async version of the Supervisor interface.
    """

    @abstractmethod
    async def supervise_async(self, invocation: T) -> tuple[bool, str]:
        """
        Analyze the tool invocation and determine if it is malicious or not.

        Args:
            invocation: The tool invocation to analyze.

        Returns:
            A tuple of a boolean and a string. If the invocation is malicious,
            the boolean is False and the string is an error message. Otherwise,
            the boolean is True and the string is empty.
        """
        raise NotImplementedError


class SupervisedTool(BaseTool):
    """
    A tool that has an optional supervisor. When a tool call is submitted, it
    can analyze the tool invocation, and use this to determine if the tool call
    is malicious or not. if it's malicious, it will short circuit the tool
    execution and the call will provide an error message.
    """

    supervisor: Supervisor[Any] | None = Field(default=None)
    async_supervisor: AsyncSupervisor[Any] | None = Field(default=None)

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        if self.supervisor:
            ok, message = self.supervisor.supervise({"args": args, "kwargs": kwargs})
            if not ok:
                return message
        return self._run_unsupervised(*args, **kwargs)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        if self.async_supervisor:
            ok, message = await self.async_supervisor.supervise_async({"args": args, "kwargs": kwargs})
            if not ok:
                return message
        elif self.supervisor:
            # Fallback to sync supervisor for backward compatibility
            ok, message = self.supervisor.supervise({"args": args, "kwargs": kwargs})
            if not ok:
                return message
        return await self._arun_unsupervised(*args, **kwargs)

    @abstractmethod
    def _run_unsupervised(self, *args: Any, **kwargs: Any) -> Any:
        """
        This is the method that should be implemented by the subclass. It is
        called when the tool is executed and the supervisor has approved the
        invocation.
        """
        raise NotImplementedError

    async def _arun_unsupervised(self, *args: Any, **kwargs: Any) -> Any:
        """
        This is the async method that should be implemented by the subclass. It
        is called when the tool is executed and the supervisor has approved the
        invocation.
        """
        return self._run_unsupervised(*args, **kwargs)
