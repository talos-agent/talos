"""
Tests for GraphLoader - Graph storage and retrieval from IPFS.
"""

from __future__ import annotations

import json

import pytest

from experimental.archon.src.graph_loader import GraphLoader
from experimental.archon.src.graph_models import StoredGraphDefinition

from .conftest import analyze_sentiment, make_decision, no_action, take_action


class TestGraphLoaderWithMockedIPFS:
    """Test GraphLoader with mocked IPFS storage."""

    def test_end_to_end_save_load(self, sentiment_graph_builder, mock_ipfs_storage, monkeypatch):
        """Test complete workflow: save graph to 'IPFS', retrieve it, and execute."""

        def mock_store(graph_json: str) -> str:
            fake_hash = f"Qm{hash(graph_json)}"
            mock_ipfs_storage[fake_hash] = graph_json
            return fake_hash

        def mock_retrieve(ipfs_hash: str) -> StoredGraphDefinition:
            json_data = mock_ipfs_storage[ipfs_hash]
            return StoredGraphDefinition.model_validate(json.loads(json_data))

        # Create loader - no credentials needed since we mock the IPFS methods
        loader = GraphLoader()
        monkeypatch.setattr(loader, "store_to_ipfs", mock_store)
        monkeypatch.setattr(loader, "retrieve_from_ipfs", mock_retrieve)

        # Step 1: Save the graph
        ipfs_hash = loader.save_graph_from_builder(
            sentiment_graph_builder,
            name="sentiment_workflow",
            description="Analyzes sentiment and takes conditional actions",
        )

        assert ipfs_hash in mock_ipfs_storage

        # Step 2: Retrieve the graph definition
        retrieved_def = loader.retrieve_from_ipfs(ipfs_hash)

        assert retrieved_def.metadata.name == "sentiment_workflow"
        assert retrieved_def.metadata.description == "Analyzes sentiment and takes conditional actions"
        assert len(retrieved_def.graph_definition.nodes) == 4

        # Step 3: Verify the serialized structure
        nodes = retrieved_def.graph_definition.nodes
        node_names = {node.name for node in nodes}
        assert node_names == {"analyze", "decide", "action", "no_action"}

        # Verify edges
        edges = retrieved_def.graph_definition.edges
        assert len(edges) >= 3

        # Verify conditional edges
        cond_edges = retrieved_def.graph_definition.conditional_edges
        assert len(cond_edges) == 1
        assert cond_edges[0].source_node == "decide"
        assert cond_edges[0].target_mapping == {
            "action": "action",
            "no_action": "no_action",
        }

        # Step 4: Verify the function references have correct structure
        # Function references should be in format "module.path:function_name"

        # Create a mapping of expected function references
        # The module will be __main__ when running tests or test_graph_loader
        expected_references = {
            "analyze": ("analyze_sentiment", analyze_sentiment),
            "decide": ("make_decision", make_decision),
            "action": ("take_action", take_action),
            "no_action": ("no_action", no_action),
        }

        # Verify each node's function reference
        for node in nodes:
            assert ":" in node.function_reference, (
                f"Invalid reference format for {node.name}: {node.function_reference}"
            )

            module_path, func_name = node.function_reference.split(":", 1)
            expected_func_name, expected_func = expected_references[node.name]

            # Verify function name matches
            assert func_name == expected_func_name, (
                f"Function name mismatch for {node.name}: expected {expected_func_name}, got {func_name}"
            )

            # Verify module path is reasonable (should be __main__ or test module)
            assert module_path in [
                "__main__",
                "test_graph_loader",
                "experimental.archon.tests.test_graph_loader",
                "experimental.archon.tests.conftest",
            ], f"Unexpected module path for {node.name}: {module_path}"

        # Verify conditional edge function reference
        assert len(cond_edges) == 1
        cond_edge = cond_edges[0]
        assert ":" in cond_edge.condition_function_reference

        cond_module, cond_func = cond_edge.condition_function_reference.split(":", 1)
        assert cond_func == "should_take_action", f"Conditional function name mismatch: {cond_func}"
        assert cond_module in [
            "__main__",
            "test_graph_loader",
            "experimental.archon.tests.test_graph_loader",
            "experimental.archon.tests.conftest",
        ], f"Unexpected module for conditional function: {cond_module}"

        # Verify that all function references are complete and valid
        all_refs = [node.function_reference for node in nodes] + [cond_edge.condition_function_reference]
        for ref in all_refs:
            # Each reference should have exactly one colon separator
            assert ref.count(":") == 1, f"Invalid reference format: {ref}"
            # Neither part should be empty
            module_part, func_part = ref.split(":")
            assert module_part, f"Empty module in reference: {ref}"
            assert func_part, f"Empty function name in reference: {ref}"

    @pytest.mark.asyncio
    async def test_save_load_and_execute_graph(self, sentiment_graph_builder, mock_ipfs_storage, monkeypatch):
        """Test that we can save a graph, load it back, and execute it successfully."""

        def mock_store(graph_json: str) -> str:
            fake_hash = f"Qm{hash(graph_json)}"
            mock_ipfs_storage[fake_hash] = graph_json
            return fake_hash

        def mock_retrieve(ipfs_hash: str) -> StoredGraphDefinition:
            json_data = mock_ipfs_storage[ipfs_hash]
            return StoredGraphDefinition.model_validate(json.loads(json_data))

        loader = GraphLoader()
        monkeypatch.setattr(loader, "store_to_ipfs", mock_store)
        monkeypatch.setattr(loader, "retrieve_from_ipfs", mock_retrieve)

        # Step 1: Save the graph to IPFS
        ipfs_hash = loader.save_graph_from_builder(
            sentiment_graph_builder,
            name="executable_workflow",
            description="Test executable workflow",
        )

        # Step 2: Load the graph back from IPFS
        recreated_graph = loader.load_graph(ipfs_hash)

        # Step 3: Execute the recreated graph with positive sentiment input
        positive_input = {
            "input_text": "This is good news!",
            "sentiment_score": 0.0,
            "decision": "",
            "final_action": "",
        }

        positive_result = await recreated_graph.ainvoke(positive_input)

        # Verify positive sentiment path
        assert positive_result["input_text"] == "This is good news!"
        assert positive_result["sentiment_score"] == 0.8  # "good" triggers positive score
        assert positive_result["decision"] == "positive"
        assert "Taking positive action" in positive_result["final_action"]
        assert "0.8" in positive_result["final_action"]

        # Step 4: Execute with negative sentiment input
        negative_input = {
            "input_text": "This is terrible news!",
            "sentiment_score": 0.0,
            "decision": "",
            "final_action": "",
        }

        negative_result = await recreated_graph.ainvoke(negative_input)

        # Verify negative sentiment path
        assert negative_result["input_text"] == "This is terrible news!"
        assert negative_result["sentiment_score"] == 0.3  # "terrible" doesn't contain "good"
        assert negative_result["decision"] == "negative"
        assert "No action needed" in negative_result["final_action"]
        assert "0.3" in negative_result["final_action"]
