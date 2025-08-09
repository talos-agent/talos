"""
LangGraph IPFS Storage Module

Provides GraphLoader class for serializing LangGraph workflows and storing them
on IPFS via Pinata for decentralized, governance-ready AI agent management.

This module combines:
- LangGraph's native graph serialization
- Pydantic models for validation and structure
- IPFS storage via Pinata for immutable, content-addressed storage
"""

from __future__ import annotations

import importlib
import os
import tempfile
from typing import Any, Awaitable, Callable, Hashable, Union

import requests
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.utils.runnable import RunnableCallable
from pinata_python.pinning import Pinning
from pydantic import BaseModel

from .graph_models import (
    ConditionalEdgeDefinition,
    ExecutionConfig,
    GraphEdgeDefinition,
    GraphMetadata,
    GraphNodeDefinition,
    SerializableGraphDefinition,
    StateChannelDefinition,
    StateSchema,
    StoredGraphDefinition,
)


class GraphLoader:
    """
    Manages serialization, IPFS storage, and deserialization of LangGraph workflows.

    Combines LangGraph's native serialization with Pydantic validation and
    IPFS storage via Pinata for decentralized, governance-ready AI workflows.

    Example:
        >>> loader = GraphLoader()
        >>> ipfs_hash = loader.save_graph(compiled_graph, "my_workflow", "Description")
        >>> recreated_graph = loader.load_graph(ipfs_hash)
    """

    def serialize_graph_from_builder(
        self,
        state_graph: StateGraph,
        name: str,
        description: str,
        created_by: str = "experimental_poc",
    ) -> str:
        """
        Serialize graph from StateGraph builder (before compilation) to capture serializable references.

        Args:
            state_graph: The StateGraph builder (before calling .compile())
            name: Name for the workflow
            description: Description of what the workflow does
            created_by: Who created this workflow

        Returns:
            JSON string representation of the serializable graph definition

        This approach extracts function references and graph structure from the StateGraph
        builder before compilation, allowing for proper deserialization.
        """
        # Extract serializable node definitions
        nodes = []
        for node_name, node_spec in state_graph.nodes.items():
            runnable = node_spec.runnable
            assert isinstance(runnable, RunnableCallable), "Only RunnableCallables are currently supported."

            if runnable.func is not None:
                func = runnable.func
            elif runnable.afunc is not None:
                func = runnable.afunc
            else:
                raise ValueError(
                    f"Node '{node_name}' has no valid function reference. "
                    f"Expected runnable.func or runnable.afunc to be set"
                )

            function_reference = f"{func.__module__}:{func.__name__}"
            nodes.append(GraphNodeDefinition(name=node_name, function_reference=function_reference))

        # Extract simple edges
        edges = []
        for edge_tuple in state_graph.edges:
            source, target = edge_tuple
            edges.append(GraphEdgeDefinition(source=source, target=target))

        # Extract conditional edges from branches
        conditional_edges = []
        branches = state_graph.branches
        for source_node, branch_dict in branches.items():
            for func_name, branch_obj in branch_dict.items():
                assert isinstance(branch_obj.path, RunnableCallable), "Only RunnableCallables are currently supported."
                if branch_obj.path.func is not None:
                    condition_func = branch_obj.path.func
                elif branch_obj.path.afunc is not None:
                    condition_func = branch_obj.path.afunc
                else:
                    raise ValueError(
                        f"Conditional edge from '{source_node}' has no valid condition function. "
                        f"Expected branch_obj.path.func or branch_obj.path.afunc to be set"
                    )

                condition_function_reference = f"{condition_func.__module__}:{condition_func.__name__}"
                conditional_edges.append(
                    ConditionalEdgeDefinition(
                        source_node=source_node,
                        condition_function_reference=condition_function_reference,
                        target_mapping=branch_obj.ends or {},
                    )
                )

        # Extract state channel information
        state_channels: list[StateChannelDefinition] = []
        if hasattr(state_graph, "state_schema"):
            # This would need to be implemented based on StateGraph internals
            pass

        # Create serializable graph definition
        serializable_def = SerializableGraphDefinition(
            nodes=nodes,
            edges=edges,
            conditional_edges=conditional_edges,
            state_channels=state_channels,
            state_type_name=state_graph.schema.__name__,
        )

        # Create state schema from the StateGraph's state schema
        state_schema = self._extract_state_schema(state_graph)

        # Create complete stored definition
        stored_definition = StoredGraphDefinition(
            metadata=GraphMetadata(
                name=name,
                description=description,
                created_by=created_by,
            ),
            graph_definition=serializable_def,
            state_schema=state_schema,
            execution_config=ExecutionConfig(),
        )

        return stored_definition.model_dump_json(indent=2)

    def _extract_state_schema(self, state_graph: StateGraph) -> StateSchema:
        """
        Extract Pydantic state schema information from StateGraph builder.

        Args:
            state_graph: StateGraph builder instance

        Returns:
            StateSchema with complete Pydantic model information

        Raises:
            ValueError: If state schema is not a Pydantic BaseModel
        """
        # Get the first (and should be only) schema class
        schema_class = next(iter(state_graph.schemas.keys()))

        assert issubclass(schema_class, BaseModel), (
            f"State schema must be a Pydantic BaseModel, got {type(schema_class)}"
        )

        class_reference = f"{schema_class.__module__}:{schema_class.__name__}"

        return StateSchema(
            name=schema_class.__name__,
            class_reference=class_reference,
        )

    def store_to_ipfs(self, graph_json: str) -> str:
        """
        Store serialized graph on IPFS via Pinata and return hash.

        Args:
            graph_json: JSON string representation of the graph

        Returns:
            IPFS hash of the stored content
        """
        api_key = os.getenv("PINATA_API_KEY")
        secret_key = os.getenv("PINATA_SECRET_API_KEY")

        if not api_key or not secret_key:
            raise ValueError("PINATA_API_KEY and PINATA_SECRET_API_KEY environment variables required for IPFS storage")

        pinata = Pinning(PINATA_API_KEY=api_key, PINATA_API_SECRET=secret_key)

        # Pin JSON content to IPFS via Pinata
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(graph_json)
            temp_path: str = f.name

        try:
            response: dict[str, Any] = pinata.pin_file_to_ipfs(temp_path)
            return response["IpfsHash"]
        finally:
            os.unlink(temp_path)

    def retrieve_from_ipfs(self, ipfs_hash: str) -> StoredGraphDefinition:
        """
        Retrieve and deserialize graph from IPFS via Pinata gateway.

        Args:
            ipfs_hash: IPFS hash of the stored graph definition

        Returns:
            StoredGraphDefinition object with validated data
        """
        gateway_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
        response = requests.get(gateway_url)
        response.raise_for_status()

        return StoredGraphDefinition.model_validate(response.json())

    def recreate_graph_from_definition(self, stored_definition: StoredGraphDefinition) -> StateGraph:
        """
        Recreate a StateGraph from its serializable definition.

        Args:
            stored_definition: StoredGraphDefinition with SerializableGraphDefinition

        Returns:
            Recreated StateGraph ready for compilation

        Note:
            This implementation dynamically imports and loads functions based on
            the serialized function references (module + name).
        """

        state_class = self._load_class_from_reference(stored_definition.state_schema.class_reference)
        assert issubclass(state_class, BaseModel), (
            f"Loaded state class must be a Pydantic BaseModel, got {type(state_class)}"
        )

        builder = StateGraph(state_class)

        for node_def in stored_definition.graph_definition.nodes:
            try:
                func = self._load_function_from_reference(node_def.function_reference)
                builder.add_node(node_def.name, func)
            except Exception as e:
                raise ImportError(f"Failed to load node {node_def.name}: {e}")

        for edge_def in stored_definition.graph_definition.edges:
            source = START if edge_def.source == "__start__" else edge_def.source
            target = END if edge_def.target == "__end__" else edge_def.target
            builder.add_edge(source, target)
        for cond_edge_def in stored_definition.graph_definition.conditional_edges:
            try:
                condition_func = self._load_function_from_reference(cond_edge_def.condition_function_reference)
                target_mapping: dict[Hashable, str] = {
                    k: END if v == "__end__" else v for k, v in cond_edge_def.target_mapping.items()
                }
                builder.add_conditional_edges(cond_edge_def.source_node, condition_func, target_mapping)
            except Exception as e:
                raise ImportError(f"Failed to load conditional edge from {cond_edge_def.source_node}: {e}")

        return builder

    def _load_function_from_reference(
        self, function_reference: str
    ) -> Union[Callable[..., Any], Callable[..., Awaitable[Any]]]:
        """
        Dynamically load a function from a module:function reference string.
        """
        try:
            module_name, function_name = function_reference.split(":", 1)
            module = importlib.import_module(module_name)
            return getattr(module, function_name)
        except (ImportError, AttributeError, ValueError) as e:
            raise ImportError(f"Could not load function from reference '{function_reference}': {e}")

    def _load_class_from_reference(self, class_reference: str) -> type:
        """
        Dynamically load a class from a module:class reference string.
        """
        try:
            module_name, class_name = class_reference.split(":", 1)
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            if not isinstance(cls, type):
                raise ValueError(f"'{class_name}' is not a class")
            return cls
        except (ImportError, AttributeError, ValueError) as e:
            raise ImportError(f"Could not load class from reference '{class_reference}': {e}")

    def recreate_graph(self, stored_definition: StoredGraphDefinition) -> CompiledGraph:
        """
        Recreate and compile a LangGraph from its stored definition.
        """
        state_graph = self.recreate_graph_from_definition(stored_definition)
        return state_graph.compile()

    def save_graph_from_builder(
        self,
        state_graph: StateGraph,
        name: str,
        description: str,
        created_by: str = "experimental_poc",
    ) -> str:
        """
        High-level method: serialize StateGraph builder and store to IPFS in one operation.

        Args:
            state_graph: The StateGraph builder (before compilation)
            name: Name for the workflow
            description: Description of what the workflow does
            created_by: Who created this workflow

        Returns:
            IPFS hash of the stored graph definition
        """
        graph_json = self.serialize_graph_from_builder(state_graph, name, description, created_by)
        return self.store_to_ipfs(graph_json)

    def load_graph(self, ipfs_hash: str) -> CompiledGraph:
        """
        High-level method: retrieve from IPFS and recreate graph in one operation.

        Args:
            ipfs_hash: IPFS hash of the stored graph definition

        Returns:
            Recreated CompiledGraph ready for execution

        Note:
            The returned graph can contain both sync and async functions.
            Use `await graph.ainvoke(input)` for execution - this works
            universally for pure sync, pure async, and mixed graphs.
        """
        stored_definition = self.retrieve_from_ipfs(ipfs_hash)
        return self.recreate_graph(stored_definition)

    def get_graph_info(self, ipfs_hash: str) -> GraphMetadata:
        """
        Get metadata about a stored graph without recreating it.
        """
        stored_definition = self.retrieve_from_ipfs(ipfs_hash)
        return stored_definition.metadata
