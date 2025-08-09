"""
Pydantic models for LangGraph workflow storage and serialization.

This module defines the data structures used for storing LangGraph workflows
on IPFS with proper validation and type safety.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Hashable

from langchain_core.runnables.graph import Edge, Node
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Immutable:
    """Mixin class that makes Pydantic models immutable using frozen=True."""

    model_config = ConfigDict(frozen=True)


class GraphModel(BaseModel, Immutable):
    """
    Base class for all graph-related models.
    """

    @staticmethod
    def _validate_function_reference(value: str) -> str:
        """Validate function reference format and security constraints."""
        if value.count(":") != 1:
            raise ValueError(
                "Function reference must be in format 'module.path:function_name' with exactly one ':' separator"
            )

        module_path, function_name = value.split(":", 1)

        if not module_path or not function_name:
            raise ValueError("Both module path and function name must be non-empty")

        # Security: No relative path components
        if ".." in module_path:
            raise ValueError("Relative path components (..) are not allowed in module path")

        # Security: Must start with 'experimental' for now
        if not module_path.startswith("experimental"):
            raise ValueError("Module path must start with 'experimental' for security")

        # Validate function name is a valid Python identifier
        if not function_name.isidentifier():
            raise ValueError(f"Function name '{function_name}' is not a valid Python identifier")

        return value


class GraphMetadata(GraphModel):
    """Metadata for a stored graph definition."""

    name: str
    version: str = "1.0.0"
    description: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    langgraph_version: str = "0.2.60"


# Note: It's a bit duplicative, but I prefer to fully separate our internal classes from LangGraph's classes.


class LangGraphNode(GraphModel):
    """Pydantic-compatible wrapper for LangGraph's Node type."""

    id: str
    name: str
    data: Any
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_langgraph_node(cls, node: Node) -> "LangGraphNode":
        """Create from a LangGraph Node."""
        return cls(id=node.id, name=node.name, data=node.data, metadata=node.metadata)

    def to_langgraph_node(self) -> Node:
        """Convert to a LangGraph Node."""
        return Node(id=self.id, name=self.name, data=self.data, metadata=self.metadata)


class LangGraphEdge(GraphModel):
    """Pydantic-compatible wrapper for LangGraph's Edge type."""

    source: str
    target: str
    data: Any | None = None
    conditional: bool = False

    @classmethod
    def from_langgraph_edge(cls, edge: Edge) -> "LangGraphEdge":
        """Create from a LangGraph Edge."""
        return cls(
            source=edge.source,
            target=edge.target,
            data=edge.data,
            conditional=edge.conditional,
        )

    def to_langgraph_edge(self) -> Edge:
        """Convert to a LangGraph Edge."""
        return Edge(
            source=self.source,
            target=self.target,
            data=self.data,
            conditional=self.conditional,
        )


class GraphNodeDefinition(GraphModel):
    """Serializable representation of a graph node before compilation."""

    name: str
    function_reference: str = Field(description="Format: 'module.path:function_name'")
    metadata: dict[str, Any] | None = None
    input_type: str | None = None

    @field_validator("function_reference")
    @classmethod
    def validate_function_reference(cls, v: str) -> str:
        return cls._validate_function_reference(v)


class GraphEdgeDefinition(GraphModel):
    """Serializable representation of a simple graph edge."""

    source: str
    target: str


class ConditionalEdgeDefinition(GraphModel):
    """Serializable representation of a conditional edge."""

    source_node: str
    condition_function_reference: str = Field(description="Format: 'module.path:function_name'")
    target_mapping: dict[Hashable, str]

    @field_validator("condition_function_reference")
    @classmethod
    def validate_condition_function_reference(cls, v: str) -> str:
        return cls._validate_function_reference(v)


class StateChannelDefinition(GraphModel):
    """Serializable representation of a state channel."""

    name: str
    channel_type: str
    default_value: Any | None = None


class SerializableGraphDefinition(GraphModel):
    """Complete serializable graph definition from StateGraph builder (before compilation)."""

    nodes: list[GraphNodeDefinition]
    edges: list[GraphEdgeDefinition]
    conditional_edges: list[ConditionalEdgeDefinition]
    state_channels: list[StateChannelDefinition]
    state_type_name: str


class StateSchema(GraphModel):
    """Pydantic-only state schema representation."""

    name: str
    class_reference: str = Field(description="Format: 'module.path:ClassName'")

    @field_validator("class_reference")
    @classmethod
    def validate_class_reference(cls, v: str) -> str:
        return cls._validate_function_reference(v)


class ExecutionConfig(GraphModel):
    """Configuration options for graph execution."""

    checkpointer: str | None = None
    debug: bool = False
    stream_mode: str = "values"
    max_iterations: int | None = None
    recursion_limit: int | None = None


class StoredGraphDefinition(GraphModel):
    """Complete stored graph definition using serializable pre-compilation data."""

    version: str = "0.0.1"
    metadata: GraphMetadata

    # Serializable graph definition from StateGraph builder (before compilation)
    graph_definition: SerializableGraphDefinition = Field(
        description="Complete serializable graph structure from StateGraph builder"
    )

    state_schema: StateSchema = Field(description="Structured information about the state schema")

    execution_config: ExecutionConfig = Field(
        default_factory=ExecutionConfig,
        description="Structured execution configuration options",
    )
