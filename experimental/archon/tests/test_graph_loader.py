"""
Tests for GraphLoader - Graph storage and retrieval from IPFS.
"""

from __future__ import annotations

from .conftest import analyze_sentiment, make_decision, no_action, take_action


class TestGraphLoaderWithMockedIPFS:
    """Test GraphLoader with mocked IPFS storage."""

    def test_end_to_end_save_load(self, sentiment_graph_builder, mock_ipfs_storage, loader_with_ipfs_mocks):
        """Test complete workflow: save graph to 'IPFS', retrieve it, and execute."""

        loader = loader_with_ipfs_mocks

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
