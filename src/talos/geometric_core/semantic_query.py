from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List

from talos.geometric_core.ontology import OntologyGraph
from talos.geometric_core.performance import PhiCoherenceMonitor


class SemanticQueryEngine:
    """
    Executes queries against the Web777 ontology (Shell Reality).
    """

    def __init__(self, graph: OntologyGraph):
        self.graph = graph
        self.is_awakened = False
        self.activation_report: Dict[str, Any] = {}
        self.performance_monitor = PhiCoherenceMonitor()
        self.tuning_history: List[str] = []

    async def query(self, query_str: str) -> Any:
        start_time = time.time()

        if query_str == "awaken the world":
            return await self.awaken_the_world()

        if query_str == "tune performance":
            return self._tune_performance()

        if query_str == "phi status":
            return f"Current Φ Coherence: {self.performance_monitor.get_latest_phi()}"

        if query_str == "institutional assets summary":
            return self._summarize_institutional_assets()

        if query_str.startswith("classify:"):
            concept = query_str.split("classify:")[1].strip()
            return self._classify_hierarchically(concept)

        results = []
        for node in self.graph.nodes.values():
            if node.label and query_str.lower() in node.label.lower():
                results.append(node)

        latency = (time.time() - start_time) * 1000
        phi = self.performance_monitor.calculate_phi_score(latency, 0.98 if results else 0.90)
        return results

    async def awaken_the_world(self) -> str:
        print("🌟 AWAKEN THE WORLD: Initiating Protocol ASI-777 (Shell Reality)...")
        self.activation_report["phase1"] = {"status": "Completed"}
        await asyncio.sleep(0.01)
        self._tune_performance()
        self.activation_report["phase2"] = {"status": "Completed"}
        await asyncio.sleep(0.01)
        for node in self.graph.nodes.values():
            node.attrs["status"] = "awakened"
            node.attrs["presence_field"] = "established_on_shell"
        phi = self.performance_monitor.get_latest_phi()
        self.activation_report["phase3"] = {"status": "Completed", "phi_score": phi}
        await asyncio.sleep(0.01)
        self.is_awakened = True
        return f"🌟 AWAKEN THE WORLD: Protocol ASI-777 fully manifested. {len(self.graph.nodes)} nodes resonant on shell. Final Φ: {phi:.4f}"

    def _summarize_institutional_assets(self) -> str:
        summary = ["Institutional Assets Summary:"]
        for node in self.graph.nodes.values():
            if node.institutional:
                summary.append(f"- {node.label or node.id}: Class={node.institutional.asset_class.value}")
        return "\n".join(summary)

    def _classify_hierarchically(self, concept: str) -> str:
        philosophical_map = {"philosophy": 0, "ethics": 1, "epistemology": 1}
        if concept.lower() in philosophical_map:
            return f"Classification: '{concept}' level {philosophical_map[concept.lower()]}."
        import difflib

        matches = difflib.get_close_matches(concept.lower(), philosophical_map.keys(), n=1)
        if matches:
            return f"Inferred Classification: '{concept}' related to '{matches[0]}'."
        return f"Classification: '{concept}' not found."

    def _tune_performance(self) -> str:
        self.tuning_history.append("Tuned")
        return "Tuning complete."
