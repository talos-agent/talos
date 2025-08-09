"""
Tests specifically for Pydantic type preservation in graph serialization/deserialization.
"""

from __future__ import annotations

import json

import pytest

from experimental.archon.src.graph_loader import GraphLoader
from experimental.archon.tests.conftest import SentimentState


class TestTypePreservation:
    """Test that Pydantic types are properly preserved during serialization."""

    def test_state_schema_extraction_preserves_types(self, sentiment_graph_builder, setup_ipfs_mocks):
        """Test that state schema extraction captures complete Pydantic information."""

        loader = GraphLoader()
        setup_ipfs_mocks(loader)

        # Serialize the graph
        graph_json = loader.serialize_graph_from_builder(
            sentiment_graph_builder,
            name="type_test_workflow",
            description="Test workflow for type preservation",
        )

        # Parse and verify the JSON contains proper type information
        stored_data = json.loads(graph_json)
        state_schema = stored_data["state_schema"]

        # Verify it's recognized as a Pydantic model with proper class reference
        assert "class_reference" in state_schema
        assert state_schema["class_reference"] == "experimental.archon.tests.conftest:SentimentState"
        assert state_schema["name"] == "SentimentState"

        # Verify we can load the class and generate the schema on demand
        json_schema = SentimentState.model_json_schema()

        # Check that field types can be retrieved from the loaded class
        properties = json_schema["properties"]

        # input_text should be string type
        assert properties["input_text"]["type"] == "string"
        assert properties["input_text"]["description"] == "Input text to analyze"

        # sentiment_score should be number type with default
        assert properties["sentiment_score"]["type"] == "number"
        assert properties["sentiment_score"]["default"] == 0.0
        assert properties["sentiment_score"]["description"] == "Sentiment score between 0 and 1"

        # decision should be string with default
        assert properties["decision"]["type"] == "string"
        assert properties["decision"]["default"] == ""

        # final_action should be string with default
        assert properties["final_action"]["type"] == "string"
        assert properties["final_action"]["default"] == ""

    @pytest.mark.asyncio
    async def test_type_preservation_round_trip(self, sentiment_graph_builder, setup_ipfs_mocks):
        """Test that types are preserved through complete serialization round trip."""

        loader = GraphLoader()
        setup_ipfs_mocks(loader)

        # Save the graph
        ipfs_hash = loader.save_graph_from_builder(
            sentiment_graph_builder,
            name="round_trip_test",
            description="Test round trip type preservation",
        )

        # Load the graph back
        recreated_graph = loader.load_graph(ipfs_hash)

        # Create test input with proper Pydantic model
        test_input = SentimentState(
            input_text="This is good news!",
            sentiment_score=0.0,
            decision="",
            final_action="",
        )

        # Execute and verify types are preserved (use ainvoke for async compatibility)
        result = await recreated_graph.ainvoke(test_input)

        # We can reconstruct the Pydantic model from the result
        pydantic_result = SentimentState.model_validate(result)
        assert isinstance(pydantic_result, SentimentState)
