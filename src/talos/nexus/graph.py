from __future__ import annotations

from langgraph.graph import StateGraph, END
from .state import NexusState


from typing import List


# Define the nodes for the graph
def node_a(state: NexusState) -> dict[str, List[str]]:
    print("Executing Node A")
    # In a real scenario, this would involve calling a tool or a service
    # For now, we just append a message to the state
    return {"messages": ["Message from Node A"]}


def node_b(state: NexusState) -> dict[str, List[str]]:
    print("Executing Node B")
    # This node will transition to the end
    return {"messages": ["Message from Node B"]}


# Create the graph
workflow = StateGraph(NexusState)

# Add the nodes to the graph
workflow.add_node("node_a", node_a)
workflow.add_node("node_b", node_b)

# Set the entrypoint and edges
workflow.set_entry_point("node_a")
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

# Compile the graph
nexus_graph = workflow.compile()
