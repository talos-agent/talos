"""
Shared test fixtures for Archon graph storage tests.
"""

from __future__ import annotations

import pytest
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


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
