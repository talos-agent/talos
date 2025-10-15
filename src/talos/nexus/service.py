from __future__ import annotations
from typing import Any, Dict, List

from .graph import nexus_graph


class NexusService:
    """
    A service for interacting with the Nexus graph.

    This service provides a simple interface for executing the Nexus graph and
    managing its state.
    """

    def __init__(self) -> None:
        self.graph = nexus_graph

    def run(self, messages: List[Any]) -> Dict[str, Any]:
        """
        Run the Nexus graph with the given messages.
        """
        return self.graph.invoke({"messages": messages})  # type: ignore
