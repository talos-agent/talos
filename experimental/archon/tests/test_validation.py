"""
Test Pydantic field validators for function references.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from experimental.archon.src.graph_models import ConditionalEdgeDefinition, GraphNodeDefinition


class TestFunctionReferenceValidation:
    """Test validation of function references."""

    def test_valid_function_reference(self):
        """Test that valid function references are accepted."""
        node = GraphNodeDefinition(
            name="test_node", function_reference="experimental.archon.tests.test_validation:test_function"
        )
        assert node.function_reference == "experimental.archon.tests.test_validation:test_function"

    def test_invalid_format_no_colon(self):
        """Test that function references without colons are rejected."""
        with pytest.raises(ValidationError, match="must be in format"):
            GraphNodeDefinition(name="test_node", function_reference="experimental.archon.tests.test_validation")

    def test_invalid_format_multiple_colons(self):
        """Test that function references with multiple colons are rejected."""
        with pytest.raises(ValidationError, match="exactly one ':' separator"):
            GraphNodeDefinition(name="test_node", function_reference="experimental.archon:test:function")

    def test_empty_module_path(self):
        """Test that empty module paths are rejected."""
        with pytest.raises(ValidationError, match="must be non-empty"):
            GraphNodeDefinition(name="test_node", function_reference=":test_function")

    def test_empty_function_name(self):
        """Test that empty function names are rejected."""
        with pytest.raises(ValidationError, match="must be non-empty"):
            GraphNodeDefinition(name="test_node", function_reference="experimental.archon.tests:")

    def test_relative_paths_rejected(self):
        """Test that relative path components are rejected."""
        with pytest.raises(ValidationError, match="Relative path components"):
            GraphNodeDefinition(name="test_node", function_reference="experimental.archon.../malicious:bad_function")

    def test_non_experimental_module_rejected(self):
        """Test that non-experimental modules are rejected."""
        with pytest.raises(ValidationError, match="must start with 'experimental'"):
            GraphNodeDefinition(name="test_node", function_reference="malicious.module:bad_function")

    def test_invalid_python_identifier(self):
        """Test that invalid Python identifiers for function names are rejected."""
        with pytest.raises(ValidationError, match="not a valid Python identifier"):
            GraphNodeDefinition(name="test_node", function_reference="experimental.archon.tests:123invalid-name")

    def test_conditional_edge_validation(self):
        """Test that conditional edges also validate function references."""
        # Valid conditional edge
        cond_edge = ConditionalEdgeDefinition(
            source_node="test_node",
            condition_function_reference="experimental.archon.tests.test_validation:condition_func",
            target_mapping={"true": "next_node", "false": "end"},
        )
        assert cond_edge.condition_function_reference == "experimental.archon.tests.test_validation:condition_func"

        # Invalid conditional edge
        with pytest.raises(ValidationError, match="must start with 'experimental'"):
            ConditionalEdgeDefinition(
                source_node="test_node",
                condition_function_reference="malicious.module:bad_condition",
                target_mapping={"true": "next_node", "false": "end"},
            )
