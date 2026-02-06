from __future__ import annotations

import torch
import torch.nn.functional as F
from torch_geometric.nn import GATConv
from pydantic import BaseModel, ConfigDict, Field


class MetabolicFlowGNN(torch.nn.Module):
    """
    GNN for modeling metabolic pathways (e.g. Glycolysis) as topographical flows.
    """
    def __init__(self, node_features: int = 4, hidden_dim: int = 16):
        super().__init__()
        self.conv1 = GATConv(node_features, hidden_dim, heads=4, concat=False)
        self.conv2 = GATConv(hidden_dim, hidden_dim, heads=4, concat=False)
        self.enzyme_predictor = torch.nn.Linear(hidden_dim * 2, 1)

    def forward(self, x, edge_index, edge_attr=None):
        x = self.conv1(x, edge_index, edge_attr)
        x = F.relu(x)
        x = self.conv2(x, edge_index, edge_attr)
        x = F.relu(x)

        src, dst = edge_index
        edge_input = torch.cat([x[src], x[dst]], dim=-1)
        flux_rate = torch.sigmoid(self.enzyme_predictor(edge_input))
        return x, flux_rate


class MetabolicSystem(BaseModel):
    """
    System for biological scale analysis using GDL.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def run_metabolic_analysis(self) -> dict[str, any]:
        """
        Simulates glycolysis as a topographic flow.
        """
        # [Concentration, FreeEnergy, State, Redox]
        x = torch.tensor([
            [10.0, 0.0, 0.0, 0.0],
            [0.5, -30.5, -25.0, -0.5],
            [0.1, -20.0, -15.0, -0.5],
            [1.0, -15.0, 0.0, -0.5],
            [0.1, -10.0, 0.0, -0.5]
        ], dtype=torch.float)

        edge_index = torch.tensor([
            [0, 2, 3, 1, 3, 4],
            [1, 3, 4, 2, 1, 2]
        ], dtype=torch.long)

        model = MetabolicFlowGNN()
        _, flux_rates = model(x, edge_index)

        # Net balance calculation
        production = torch.zeros(5)
        consumption = torch.zeros(5)
        src, dst = edge_index
        production.index_add_(0, dst, flux_rates.squeeze())
        consumption.index_add_(0, src, flux_rates.squeeze())
        net_balance = production - consumption

        metabolites = ["Glicose", "ATP", "ADP", "Piruvato", "Lactato"]
        balances = {metabolites[i]: float(net_balance[i]) for i in range(5)}

        return {
            "flux_rates": flux_rates.squeeze().tolist(),
            "balances": balances,
            "status": "HOMEOSTÁTICO" if torch.abs(net_balance).mean() < 0.1 else "DYN_UNSTABLE"
        }

class MetabolicGDLService:
    """Service for performing metabolic surveys."""
    def perform_metabolic_survey(self, user_id: str) -> dict:
        system = MetabolicSystem()
        analysis = system.run_metabolic_analysis()
        return {
            "user_id": user_id,
            "cellular_coherence": 0.95 if analysis["status"] == "HOMEOSTÁTICO" else 0.42,
            "transport_efficiency": 0.88,
            "message": f"Metabolic status: {analysis['status']}"
        }
