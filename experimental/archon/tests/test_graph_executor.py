"""
Tests for GraphExecutor - Graph execution from IPFS-stored definitions.
"""

from __future__ import annotations

import json

import pytest

from experimental.archon.src.graph_executor import GraphExecutor
from experimental.archon.src.graph_models import StoredGraphDefinition


class TestGraphExecutorWithMockedIPFS:
    """Test GraphExecutor with mocked IPFS storage."""

    @pytest.mark.asyncio
    async def test_execute_stored_graph(self, sentiment_graph_builder, mock_ipfs_storage, monkeypatch):
        """Test that we can execute a stored graph through the executor."""

        def mock_store(graph_json: str) -> str:
            fake_hash = f"Qm{hash(graph_json)}"
            mock_ipfs_storage[fake_hash] = graph_json
            return fake_hash

        def mock_retrieve(ipfs_hash: str) -> StoredGraphDefinition:
            json_data = mock_ipfs_storage[ipfs_hash]
            return StoredGraphDefinition.model_validate(json.loads(json_data))

        executor = GraphExecutor()

        # Use monkeypatch to replace methods - this is type-safe
        monkeypatch.setattr(executor.loader, "store_to_ipfs", mock_store)
        monkeypatch.setattr(executor.loader, "retrieve_from_ipfs", mock_retrieve)

        # Step 1: Store the graph using the underlying loader
        ipfs_hash = executor.loader.save_graph_from_builder(
            sentiment_graph_builder,
            name="executor_test_workflow",
            description="Test workflow for executor",
        )

        # Step 2: Execute the stored graph with positive sentiment input
        positive_input = {
            "input_text": "This is good news!",
            "sentiment_score": 0.0,
            "decision": "",
            "final_action": "",
        }

        positive_result = await executor.execute_graph(ipfs_hash, positive_input)

        # Verify positive sentiment path
        assert positive_result["input_text"] == "This is good news!"
        assert positive_result["sentiment_score"] == 0.8  # "good" triggers positive score
        assert positive_result["decision"] == "positive"
        assert "Taking positive action" in positive_result["final_action"]
        assert "0.8" in positive_result["final_action"]

        # Step 3: Execute with negative sentiment input
        negative_input = {
            "input_text": "This is terrible news!",
            "sentiment_score": 0.0,
            "decision": "",
            "final_action": "",
        }

        negative_result = await executor.execute_graph(ipfs_hash, negative_input)

        # Verify negative sentiment path
        assert negative_result["input_text"] == "This is terrible news!"
        assert negative_result["sentiment_score"] == 0.3  # "terrible" doesn't contain "good"
        assert negative_result["decision"] == "negative"
        assert "No action needed" in negative_result["final_action"]
        assert "0.3" in negative_result["final_action"]

    @pytest.mark.asyncio
    async def test_type_aware_execution(self, sentiment_graph_builder, mock_ipfs_storage, monkeypatch):
        """Test the new type-aware LoadedGraph functionality."""

        def mock_store(graph_json: str) -> str:
            fake_hash = f"Qm{hash(graph_json)}"
            mock_ipfs_storage[fake_hash] = graph_json
            return fake_hash

        def mock_retrieve(ipfs_hash: str) -> StoredGraphDefinition:
            json_data = mock_ipfs_storage[ipfs_hash]
            return StoredGraphDefinition.model_validate(json.loads(json_data))

        executor = GraphExecutor()
        monkeypatch.setattr(executor.loader, "store_to_ipfs", mock_store)
        monkeypatch.setattr(executor.loader, "retrieve_from_ipfs", mock_retrieve)

        # Store the graph
        ipfs_hash = executor.loader.save_graph_from_builder(
            sentiment_graph_builder,
            name="type_aware_test",
            description="Test type-aware execution",
        )

        # Load the graph with type information
        loaded_graph = executor.load_graph(ipfs_hash)

        # Verify we have access to the state class
        assert hasattr(loaded_graph, "state_class")
        assert loaded_graph.state_class.__name__ == "SentimentState"

        # Create typed input using the state class
        typed_input = loaded_graph.create_state(
            input_text="This is good news!",
            sentiment_score=0.0,
            decision="",
            final_action="",
        )

        # Verify the created state is properly typed
        from experimental.archon.tests.conftest import SentimentState

        assert isinstance(typed_input, SentimentState)
        assert typed_input.input_text == "This is good news!"

        # Execute with the Pydantic model directly
        result = await loaded_graph.execute(typed_input)

        # Validate and convert result back to typed state
        typed_result = loaded_graph.validate_result(result)

        assert isinstance(typed_result, SentimentState)
        assert typed_result.input_text == "This is good news!"
        assert typed_result.sentiment_score == 0.8  # "good" triggers positive score
        assert typed_result.decision == "positive"
        assert "Taking positive action" in typed_result.final_action
