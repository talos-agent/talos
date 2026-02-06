from __future__ import annotations

from typing import Any, ClassVar, Optional

from pydantic import ConfigDict, Field

from talos.geometric_core.ontology import OntologyGraph, OntologyNode
from talos.geometric_core.semantic_query import SemanticQueryEngine
from talos.skills.base import Skill


class Web777Skill(Skill):
    """
    A skill for interacting with the Web777 Ontology Engine (Resonant Shell).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: ClassVar[str] = "web777"
    description: ClassVar[str] = "Query and manage the Web777 ontology."

    graph: OntologyGraph = Field(default_factory=OntologyGraph)
    query_engine: Optional[SemanticQueryEngine] = None

    def model_post_init(self, __context: Any) -> None:
        self.query_engine = SemanticQueryEngine(self.graph)

    async def run_async(self, **kwargs: Any) -> Any:
        if "query" in kwargs:
            return await self.query(kwargs["query"])
        if "add_node" in kwargs:
            node_data = kwargs["add_node"]
            node = OntologyNode(**node_data)
            self.graph.add_node(node)
            return f"Node {node.id} added to Web777 ontology."
        return "No valid Web777 action provided."

    def run(self, **kwargs: Any) -> Any:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            return asyncio.run_coroutine_threadsafe(self.run_async(**kwargs), loop).result()
        else:
            return asyncio.run(self.run_async(**kwargs))

    async def query(self, query_str: str) -> Any:
        if not self.query_engine:
            self.query_engine = SemanticQueryEngine(self.graph)
        return await self.query_engine.query(query_str)
