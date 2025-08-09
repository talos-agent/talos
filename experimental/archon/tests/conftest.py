"""
Shared test fixtures for Archon graph storage tests.
"""

from __future__ import annotations

import json
from typing import Any, Callable

import pytest
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from experimental.archon.src.graph_loader import GraphLoader
from experimental.archon.src.graph_models import StoredGraphDefinition


class SentimentState(BaseModel):
    """Pydantic state model for sentiment analysis workflow."""

    input_text: str = Field(description="Input text to analyze")
    sentiment_score: float = Field(default=0.0, description="Sentiment score between 0 and 1")
    decision: str = Field(default="", description="Decision based on sentiment analysis")
    final_action: str = Field(default="", description="Final action taken based on decision")


def analyze_sentiment(state: SentimentState) -> SentimentState:
    """Mock sentiment analysis node."""
    text = state.input_text
    mock_score = 0.8 if "good" in text.lower() else 0.3
    return state.model_copy(update={"sentiment_score": mock_score})


async def make_decision(state: SentimentState) -> SentimentState:
    """Decision node based on sentiment score."""
    decision = "positive" if state.sentiment_score > 0.6 else "negative"
    return state.model_copy(update={"decision": decision})


def take_action(state: SentimentState) -> SentimentState:
    """Action node for positive sentiment."""
    action = f"Taking positive action based on score {state.sentiment_score}"
    return state.model_copy(update={"final_action": action})


def no_action(state: SentimentState) -> SentimentState:
    """No action node for negative sentiment."""
    action = f"No action needed, score too low: {state.sentiment_score}"
    return state.model_copy(update={"final_action": action})


def should_take_action(state: SentimentState) -> str:
    """Conditional edge function to decide next node."""
    return "action" if state.decision == "positive" else "no_action"


@pytest.fixture
def sentiment_graph_builder() -> StateGraph:
    """
    Create the sentiment analysis graph from the POC.
    Returns the StateGraph builder (before compilation).
    """
    builder = StateGraph(SentimentState)

    # Add nodes
    builder.add_node("analyze", analyze_sentiment)
    builder.add_node("decide", make_decision)
    builder.add_node("action", take_action)
    builder.add_node("no_action", no_action)

    # Add edges
    builder.add_edge(START, "analyze")
    builder.add_edge("analyze", "decide")
    builder.add_conditional_edges("decide", should_take_action, {"action": "action", "no_action": "no_action"})
    builder.add_edge("action", END)
    builder.add_edge("no_action", END)

    return builder


@pytest.fixture
def mock_ipfs_storage():
    """
    Create an in-memory storage to mock IPFS.
    Returns a dictionary that will store graph definitions by hash.
    """
    return {}


class IPFSMockHelpers:
    """Helper functions for mocking IPFS operations."""

    @staticmethod
    def create_mock_store(storage: dict[str, str]) -> Callable[[str], str]:
        """Create a mock store function that saves to the provided storage."""

        def mock_store(graph_json: str) -> str:
            fake_hash = f"Qm{hash(graph_json)}"
            storage[fake_hash] = graph_json
            return fake_hash

        return mock_store

    @staticmethod
    def create_mock_retrieve(storage: dict[str, str]) -> Callable[[str], StoredGraphDefinition]:
        """Create a mock retrieve function that loads from the provided storage."""

        def mock_retrieve(ipfs_hash: str) -> StoredGraphDefinition:
            json_data = storage[ipfs_hash]
            return StoredGraphDefinition.model_validate(json.loads(json_data))

        return mock_retrieve


@pytest.fixture
def mock_ipfs_functions(mock_ipfs_storage):
    """
    Provide mock IPFS store and retrieve functions.
    Returns a tuple of (mock_store, mock_retrieve) functions.
    """
    mock_store = IPFSMockHelpers.create_mock_store(mock_ipfs_storage)
    mock_retrieve = IPFSMockHelpers.create_mock_retrieve(mock_ipfs_storage)
    return mock_store, mock_retrieve


@pytest.fixture
def setup_ipfs_mocks(monkeypatch, mock_ipfs_functions):
    """
    Fixture that sets up IPFS mocks for a GraphLoader or GraphExecutor.
    Returns a function that applies the mocks to a given loader/executor.
    """
    mock_store, mock_retrieve = mock_ipfs_functions

    def apply_mocks(obj: Any) -> None:
        """Apply IPFS mocks to a GraphLoader or GraphExecutor instance."""
        if hasattr(obj, "loader"):  # GraphExecutor
            target = obj.loader
        else:  # GraphLoader
            target = obj

        monkeypatch.setattr(target, "store_to_ipfs", mock_store)
        monkeypatch.setattr(target, "retrieve_from_ipfs", mock_retrieve)

    return apply_mocks


@pytest.fixture
def loader_with_ipfs_mocks(setup_ipfs_mocks):
    """
    Create a GraphLoader with IPFS mocks already applied.
    This fixture can be used directly instead of creating and mocking separately.
    """
    loader = GraphLoader()
    setup_ipfs_mocks(loader)
    return loader


@pytest.fixture
def executor_with_ipfs_mocks(setup_ipfs_mocks):
    """
    Create a GraphExecutor with IPFS mocks already applied.
    This fixture can be used directly instead of creating and mocking separately.
    """
    from experimental.archon.src.graph_executor import GraphExecutor

    executor = GraphExecutor()
    setup_ipfs_mocks(executor)
    return executor
