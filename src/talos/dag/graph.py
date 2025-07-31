from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, ConfigDict

from talos.dag.nodes import DAGNode, GraphState


class TalosDAG(BaseModel):
    """Main DAG class that manages the LangGraph StateGraph."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    description: Optional[str] = None
    nodes: Dict[str, DAGNode] = {}
    edges: List[tuple[str, str]] = []
    conditional_edges: Dict[str, Dict[str, str]] = {}
    graph: Optional[StateGraph] = None
    compiled_graph: Optional[Any] = None
    
    def add_node(self, node: DAGNode) -> None:
        """Add a node to the DAG."""
        self.nodes[node.node_id] = node
        self._rebuild_graph()
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the DAG."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.edges = [(src, dst) for src, dst in self.edges if src != node_id and dst != node_id]
            self.conditional_edges = {k: v for k, v in self.conditional_edges.items() if k != node_id}
            self._rebuild_graph()
            return True
        return False
    
    def add_edge(self, source: str, destination: str) -> None:
        """Add a direct edge between two nodes."""
        self.edges.append((source, destination))
        self._rebuild_graph()
    
    def add_conditional_edge(self, source: str, conditions: Dict[str, str]) -> None:
        """Add conditional edges from a source node."""
        self.conditional_edges[source] = conditions
        self._rebuild_graph()
    
    def _rebuild_graph(self) -> None:
        """Rebuild the LangGraph StateGraph from current nodes and edges."""
        if not self.nodes:
            return
        
        self.graph = StateGraph(GraphState)
        
        for node_id, node in self.nodes.items():
            self.graph.add_node(node_id, node.execute)
        
        for source, destination in self.edges:
            if source in self.nodes and destination in self.nodes:
                self.graph.add_edge(source, destination)
        
        for source, conditions in self.conditional_edges.items():
            if source in self.nodes:
                def route_function(state: GraphState) -> str:
                    next_node = state.get("context", {}).get("next_node", "default")
                    return conditions.get(next_node, END)
                
                self.graph.add_conditional_edges(
                    source,
                    route_function,
                    list(conditions.values())
                )
        
        if self.nodes:
            first_node = next(iter(self.nodes.keys()))
            self.graph.add_edge(START, first_node)
        
        self.compiled_graph = self.graph.compile()
    
    def execute(self, initial_state: GraphState) -> GraphState:
        """Execute the DAG with the given initial state."""
        if not self.compiled_graph:
            self._rebuild_graph()
        
        if not self.compiled_graph:
            raise ValueError("No compiled graph available for execution")
        
        result = self.compiled_graph.invoke(initial_state)
        return result
    
    def get_graph_config(self) -> Dict[str, Any]:
        """Get the complete graph configuration for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "nodes": {node_id: node.get_node_config() for node_id, node in self.nodes.items()},
            "edges": self.edges,
            "conditional_edges": self.conditional_edges,
            "metadata": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "conditional_edge_count": len(self.conditional_edges)
            }
        }
    
    def serialize_to_json(self) -> str:
        """Serialize the DAG configuration to JSON for on-chain storage."""
        config = self.get_graph_config()
        return json.dumps(config, indent=2)
    
    def visualize_graph(self) -> str:
        """Return a text representation of the graph structure."""
        lines = [f"DAG: {self.name}"]
        if self.description:
            lines.append(f"Description: {self.description}")
        
        lines.append("\nNodes:")
        for node_id, node in self.nodes.items():
            lines.append(f"  - {node_id} ({node.node_type}): {node.name}")
        
        lines.append("\nEdges:")
        for source, destination in self.edges:
            lines.append(f"  - {source} -> {destination}")
        
        if self.conditional_edges:
            lines.append("\nConditional Edges:")
            for source, conditions in self.conditional_edges.items():
                lines.append(f"  - {source}:")
                for condition, target in conditions.items():
                    lines.append(f"    - {condition} -> {target}")
        
        return "\n".join(lines)


class DAGProposal(BaseModel):
    """Proposal for modifying the DAG structure."""
    
    proposal_id: str
    title: str
    description: str
    proposed_changes: Dict[str, Any]
    rationale: str
    impact_assessment: str
    
    def apply_to_dag(self, dag: TalosDAG) -> TalosDAG:
        """Apply the proposed changes to a DAG."""
        changes = self.proposed_changes
        
        if "add_nodes" in changes:
            for node_config in changes["add_nodes"]:
                pass
        
        if "remove_nodes" in changes:
            for node_id in changes["remove_nodes"]:
                dag.remove_node(node_id)
        
        if "add_edges" in changes:
            for edge in changes["add_edges"]:
                dag.add_edge(edge["source"], edge["destination"])
        
        if "remove_edges" in changes:
            for edge in changes["remove_edges"]:
                dag.edges = [(s, d) for s, d in dag.edges if not (s == edge["source"] and d == edge["destination"])]
        
        dag._rebuild_graph()
        return dag
