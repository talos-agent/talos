from __future__ import annotations

from typing import TypedDict

from langchain_core.messages import BaseMessage


class NexusState(TypedDict):
    """
    Represents the state of the Nexus graph.

    Attributes:
        messages: The list of messages that have been exchanged.
        next: The next node to execute.
    """

    messages: list[BaseMessage]
    next: str
