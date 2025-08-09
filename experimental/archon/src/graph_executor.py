"""
LangGraph Executor Module

Provides GraphExecutor class for loading and executing stored graphs from IPFS.
This encapsulates the process of retrieving a graph by its IPFS hash and running
it with provided input, handling both sync and async execution automatically.
"""

from __future__ import annotations

from typing import Any, Union

from langgraph.graph.graph import CompiledGraph
from pydantic import BaseModel

from .graph_loader import GraphLoader


class LoadedGraph:
    """Container for a loaded graph with its state class."""

    def __init__(self, compiled_graph: CompiledGraph, state_class: type[BaseModel]):
        self.compiled_graph = compiled_graph
        self.state_class = state_class

    async def execute(self, input_state: Union[BaseModel, dict[str, Any]]) -> dict[str, Any]:
        """Execute the graph with type-aware input handling."""
        # Convert Pydantic model to dict if needed (LangGraph expects dict)
        if isinstance(input_state, BaseModel):
            state_dict = input_state.model_dump()
        else:
            state_dict = input_state

        return await self.compiled_graph.ainvoke(state_dict)

    def create_state(self, **kwargs) -> BaseModel:
        """Create a properly typed state instance."""
        return self.state_class(**kwargs)

    def validate_result(self, result: dict[str, Any]) -> BaseModel:
        """Validate and convert result dict back to typed state."""
        return self.state_class.model_validate(result)


class GraphExecutor:
    """
    Executes stored LangGraph workflows loaded from IPFS with enhanced type safety.

    Provides both simple execution and advanced type-aware methods.

    Example:
        >>> executor = GraphExecutor()
        >>> # Simple execution
        >>> result = await executor.execute_graph(ipfs_hash, {"input": "data"})
        >>>
        >>> # Type-aware execution
        >>> loaded = executor.load_graph(ipfs_hash)
        >>> state = loaded.create_state(input_text="Hello world!")
        >>> result_dict = await loaded.execute(state)
        >>> typed_result = loaded.validate_result(result_dict)
    """

    def __init__(self) -> None:
        """Initialize the GraphExecutor with a GraphLoader instance."""
        self.loader = GraphLoader()

    def load_graph(self, ipfs_hash: str) -> LoadedGraph:
        """
        Load a graph and expose its state class for type-safe usage.

        Args:
            ipfs_hash: IPFS hash of the stored graph definition

        Returns:
            LoadedGraph with both compiled graph and state class

        Raises:
            ImportError: If graph functions or state class cannot be loaded
            ValueError: If graph structure is invalid
        """
        # Load the stored definition first to get state class
        stored_definition = self.loader.retrieve_from_ipfs(ipfs_hash)
        state_class = self.loader._load_class_from_reference(stored_definition.state_schema.class_reference)

        # Load the compiled graph
        compiled_graph = self.loader.load_graph(ipfs_hash)

        return LoadedGraph(compiled_graph, state_class)

    async def execute_graph(self, ipfs_hash: str, input_state: dict[str, Any]) -> dict[str, Any]:
        """
        Load and execute a graph from IPFS with the given input state.

        Args:
            ipfs_hash: IPFS hash of the stored graph definition
            input_state: Input state dictionary matching the graph's state schema

        Returns:
            Final state dictionary after graph execution

        Raises:
            ImportError: If graph functions cannot be loaded
            ValueError: If graph structure is invalid
            Exception: If graph execution fails

        Note:
            This method always uses async execution (ainvoke) which works
            universally for sync, async, and mixed graphs.
        """
        loaded_graph = self.load_graph(ipfs_hash)
        return await loaded_graph.execute(input_state)
