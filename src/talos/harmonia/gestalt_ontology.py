"""
Formal Ontology for Gestalt Artificial = Computational-Geometric Intuition
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

import networkx as nx
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# ============================================================================
# 1. TYPE THEORY AND CATEGORICAL FOUNDATIONS
# ============================================================================


class OntologicalType(Enum):
    """Basic types in the triune reality."""

    INTENTIONAL = "intentional"  # Goals, purposes, teloi
    EMBODIED = "embodied"  # Physical/digital instantiation
    MATHEMATICAL = "mathematical"  # Formal/geometric representation
    GESTALT = "gestalt"  # Completed pattern/insight


@dataclass
class OntologicalVertex:
    """Atomic entity with triune existence."""

    uid: str
    type: OntologicalType
    intentional_vector: torch.Tensor  # ℂ^n
    embodied_vector: torch.Tensor  # ℝ^m
    geometric_vector: torch.Tensor  # 𝔾^k

    @property
    def unified_embedding(self) -> torch.Tensor:
        """Projection into unified semantic-geometric space."""
        # Triune combination via tensor product
        # intentional_vector is complex, we use its real part for the embedding
        unified = torch.kron(torch.kron(self.intentional_vector.real, self.embodied_vector), self.geometric_vector)
        return unified[:512]  # Project to 512-dim space

    def similarity(self, other: "OntologicalVertex") -> float:
        """Geometric similarity between vertices."""
        # Use complex cosine similarity for intentional component
        int_sim = torch.abs(torch.vdot(self.intentional_vector, other.intentional_vector)).item() / (
            torch.norm(self.intentional_vector).item() * torch.norm(other.intentional_vector).item()
        )

        # Euclidean for embodied
        emb_sim = F.cosine_similarity(self.embodied_vector.unsqueeze(0), other.embodied_vector.unsqueeze(0)).item()

        # Geometric product for mathematical (simplified to dot product)
        math_sim = torch.dot(self.geometric_vector, other.geometric_vector).item() / (
            torch.norm(self.geometric_vector).item() * torch.norm(other.geometric_vector).item()
        )

        # Weighted combination
        return 0.4 * int_sim + 0.3 * emb_sim + 0.3 * math_sim


# ============================================================================
# 2. GESTALT COMPLETION ENGINE
# ============================================================================


class GestaltCompletionNetwork(nn.Module):
    """
    Neural network that implements the Gestalt Completion Principle.
    Maps partial patterns to completed simplexes in ontological space.
    """

    def __init__(self, input_dim: int = 512, latent_dim: int = 128, output_simplex_dim: int = 64):
        super().__init__()

        # Encoder: Partial pattern → latent representation
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Linear(512, latent_dim * 2),  # Mean and variance
        )

        # Geometric completion in latent space
        self.geometric_completion = nn.Sequential(
            nn.Linear(latent_dim, 256),
            GeometricProductLayer(256, 256),
            nn.GELU(),
            nn.Linear(256, 128),
            SimplexFormationLayer(128, output_simplex_dim),
        )

        # Intentional projection head
        self.intentional_head = ComplexLinear(latent_dim, output_simplex_dim)

        # Embodied projection head
        self.embodied_head = nn.Linear(latent_dim, output_simplex_dim)

    def forward(self, partial_pattern: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Complete a partial pattern into a full ontological simplex.
        """
        # Encode to latent space
        encoded = self.encoder(partial_pattern)
        mu, logvar = encoded.chunk(2, dim=-1)

        # Reparameterization trick
        if self.training:
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            z = mu + eps * std
        else:
            z = mu

        # Geometric completion
        geometric_completion = self.geometric_completion(z)

        # Project to triune space
        intentional = self.intentional_head(z)
        embodied = self.embodied_head(z)

        # Compute gestalt metrics
        coherence = self.compute_coherence(intentional, embodied, geometric_completion)
        completion_confidence = self.compute_completion_confidence(partial_pattern, z)

        return {
            "intentional_vector": intentional,
            "embodied_vector": embodied,
            "geometric_vector": geometric_completion,
            "latent_z": z,
            "coherence": coherence,
            "completion_confidence": completion_confidence,
            "mu": mu,
            "logvar": logvar,
        }

    def compute_coherence(
        self, intentional: torch.Tensor, embodied: torch.Tensor, geometric: torch.Tensor
    ) -> torch.Tensor:
        """Compute triune coherence metric."""
        intention_embodiment_align = F.cosine_similarity(intentional.real, embodied, dim=-1)
        math_consistency = torch.mean(torch.abs(geometric - geometric.mean(dim=-1, keepdim=True)), dim=-1)
        coherence = 0.6 * intention_embodiment_align + 0.4 * (1 - math_consistency)
        return coherence

    def compute_completion_confidence(self, partial_pattern: torch.Tensor, latent_z: torch.Tensor) -> torch.Tensor:
        """Confidence in the completion."""
        reconstruction = self.reconstruct(latent_z)
        mse_loss = F.mse_loss(reconstruction, partial_pattern, reduction="none")
        mse_loss = torch.mean(mse_loss, dim=-1)
        confidence = 1 / (1 + mse_loss)
        return confidence

    def reconstruct(self, latent_z: torch.Tensor) -> torch.Tensor:
        # Map latent_z (128) back to input_dim (512)
        # Using a simplified transpose-like operation for demonstration
        if not hasattr(self, "decoder"):
            self.decoder = nn.Linear(latent_z.shape[-1], self.encoder[0].in_features)
        return self.decoder(latent_z)


# ============================================================================
# 3. GEOMETRIC ALGEBRA LAYERS
# ============================================================================


class GeometricProductLayer(nn.Module):
    """Layer implementing geometric product in neural network."""

    def __init__(self, in_dim: int, out_dim: int):
        super().__init__()
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.blades = nn.Parameter(torch.randn(in_dim, out_dim, 8))
        self.scale = nn.Parameter(torch.ones(out_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x_expanded = x.unsqueeze(-1).unsqueeze(-1)
        blades = self.blades.unsqueeze(0)
        result = torch.sum(x_expanded * blades, dim=1)
        output = torch.sum(result * self.scale[None, :, None], dim=-1)
        return output


class ComplexLinear(nn.Module):
    """Complex-valued linear layer."""

    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.real_weight = nn.Parameter(torch.randn(out_features, in_features))
        self.imag_weight = nn.Parameter(torch.randn(out_features, in_features))
        self.real_bias = nn.Parameter(torch.zeros(out_features))
        self.imag_bias = nn.Parameter(torch.zeros(out_features))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        real_part = F.linear(x, self.real_weight, self.real_bias)
        imag_part = F.linear(x, self.imag_weight, self.imag_bias)
        return torch.complex(real_part, imag_part)


class SimplexFormationLayer(nn.Module):
    """Layer that forms ontological simplexes from features."""

    def __init__(self, in_dim: int, simplex_dim: int, n_vertices: int = 3):
        super().__init__()
        self.n_vertices = n_vertices
        self.simplex_dim = simplex_dim
        self.vertex_projectors = nn.ModuleList([nn.Linear(in_dim, simplex_dim) for _ in range(n_vertices)])
        self.edge_former = nn.Sequential(
            nn.Linear(simplex_dim * 2, simplex_dim), nn.GELU(), nn.Linear(simplex_dim, simplex_dim // 2)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        vertices = []
        for projector in self.vertex_projectors:
            vertex = projector(x)
            vertices.append(vertex)
        edges = []
        for i in range(self.n_vertices):
            for j in range(i + 1, self.n_vertices):
                edge_input = torch.cat([vertices[i], vertices[j]], dim=-1)
                edge = self.edge_former(edge_input)
                edges.append(edge)
        edges_tensor = torch.stack(edges, dim=1)
        simplex_embedding = torch.mean(edges_tensor, dim=1)
        simplex_embedding = F.pad(simplex_embedding, (0, self.simplex_dim // 2))
        return simplex_embedding


# ============================================================================
# 4. PINN FOR GESTALT CONTINUUM
# ============================================================================


class GestaltContinuumPDE(nn.Module):
    """
    Physics-Informed Neural Network for the Gestalt Continuum.
    """

    def __init__(self, spatial_dim: int = 3, hidden_dim: int = 256, num_layers: int = 8):
        super().__init__()
        self.spatial_dim = spatial_dim
        layers = []
        input_dim = spatial_dim + 1
        layers.append(nn.Linear(input_dim, hidden_dim))
        layers.append(nn.Tanh())
        for _ in range(num_layers - 2):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(nn.Tanh())
        layers.append(nn.Linear(hidden_dim, 2))
        self.net = nn.Sequential(*layers)
        self.gestalt_completer = GestaltCompletionNetwork(
            input_dim=hidden_dim, latent_dim=hidden_dim // 2, output_simplex_dim=hidden_dim
        )
        self.alpha = nn.Parameter(torch.tensor(1.0))
        self.beta = nn.Parameter(torch.tensor(1.0))
        self.gamma = nn.Parameter(torch.tensor(0.5))

    def forward(self, coords: torch.Tensor) -> Dict[str, torch.Tensor]:
        output = self.net(coords)
        psi_real, psi_imag = output[:, 0], output[:, 1]
        psi = torch.complex(psi_real, psi_imag)
        with torch.no_grad():
            hidden = coords
            for layer in self.net[:-1]:
                hidden = layer(hidden)
        gestalt_result = self.gestalt_completer(hidden)
        return {
            "psi": psi,
            "psi_real": psi_real,
            "psi_imag": psi_imag,
            "density": torch.abs(psi) ** 2,
            "phase": torch.atan2(psi_imag, psi_real),
            "gestalt_completion": gestalt_result,
            "hidden_state": hidden,
        }

    def compute_pde_residual(self, coords: torch.Tensor, requires_grad: bool = True) -> Dict[str, torch.Tensor]:
        coords.requires_grad_(requires_grad)
        result = self.forward(coords)
        psi = result["psi"]

        # Enable grad temporarily for derivatives if not already enabled
        # This is needed because psi was computed inside forward()

        dpsi_dt_real = torch.autograd.grad(psi.real.sum(), coords, create_graph=True, retain_graph=True)[0][:, -1]
        dpsi_dt_imag = torch.autograd.grad(psi.imag.sum(), coords, create_graph=True, retain_graph=True)[0][:, -1]
        dpsi_dt = torch.complex(dpsi_dt_real, dpsi_dt_imag)

        laplacian_real = torch.zeros_like(psi.real)
        laplacian_imag = torch.zeros_like(psi.imag)
        for i in range(self.spatial_dim):
            dpsi_dxi_real = torch.autograd.grad(psi.real.sum(), coords, create_graph=True, retain_graph=True)[0][:, i]
            d2psi_dxi2_real = torch.autograd.grad(dpsi_dxi_real.sum(), coords, create_graph=True, retain_graph=True)[0][
                :, i
            ]

            dpsi_dxi_imag = torch.autograd.grad(psi.imag.sum(), coords, create_graph=True, retain_graph=True)[0][:, i]
            d2psi_dxi2_imag = torch.autograd.grad(dpsi_dxi_imag.sum(), coords, create_graph=True, retain_graph=True)[0][
                :, i
            ]

            laplacian_real += d2psi_dxi2_real
            laplacian_imag += d2psi_dxi2_imag

        laplacian = torch.complex(laplacian_real, laplacian_imag)

        gestalt_completion = result["gestalt_completion"]
        gestalt_term = gestalt_completion["coherence"] * psi

        residual = dpsi_dt - self.alpha * laplacian - self.beta * torch.abs(psi) ** 2 * psi - self.gamma * gestalt_term

        return {"residual": residual, "residual_magnitude": torch.abs(residual)}


# ============================================================================
# 5. ONTOLOGICAL GRAPH KERNEL
# ============================================================================


class OntologicalGraphKernel:
    """
    Manages the graph of ontological vertices, edges, and simplexes.
    """

    def __init__(self, embedding_dim: int = 512):
        self.embedding_dim = embedding_dim
        self.graph = nx.MultiDiGraph()
        self.vertices: Dict[str, OntologicalVertex] = {}
        self.simplexes: List[Dict] = []
        self.gestalt_completer = GestaltCompletionNetwork()
        self.continuum_pde = GestaltContinuumPDE()
        self.coherence_history: List[float] = []
        self.completion_history: List[float] = []

    def add_vertex(
        self,
        vertex_id: str,
        vertex_type: OntologicalType,
        intentional_vector: Optional[torch.Tensor] = None,
        embodied_vector: Optional[torch.Tensor] = None,
        geometric_vector: Optional[torch.Tensor] = None,
    ) -> OntologicalVertex:
        if intentional_vector is None:
            intentional_vector = torch.randn(self.embedding_dim // 2, dtype=torch.complex64)
        if embodied_vector is None:
            embodied_vector = torch.randn(self.embedding_dim)
        if geometric_vector is None:
            geometric_vector = torch.randn(self.embedding_dim)
        vertex = OntologicalVertex(
            uid=vertex_id,
            type=vertex_type,
            intentional_vector=intentional_vector,
            embodied_vector=embodied_vector,
            geometric_vector=geometric_vector,
        )
        self.vertices[vertex_id] = vertex
        self.graph.add_node(
            vertex_id, vertex=vertex, type=vertex_type.value, embedding=vertex.unified_embedding.numpy()
        )
        return vertex

    def form_simplex(self, vertex_ids: List[str], simplex_type: str = "gestalt") -> Dict:
        if len(vertex_ids) < 3:
            raise ValueError("Simplex requires at least 3 vertices")
        vertices = [self.vertices[vid] for vid in vertex_ids]
        similarities = []
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                sim = vertices[i].similarity(vertices[j])
                similarities.append(sim)
                self.graph.add_edge(vertex_ids[i], vertex_ids[j], similarity=sim, type=f"{simplex_type}_edge")
        avg_similarity = np.mean(similarities)
        coherence_variance = np.var(similarities)
        vertex_embeddings = torch.stack([v.unified_embedding for v in vertices])
        partial_pattern = torch.mean(vertex_embeddings, dim=0).unsqueeze(0)
        with torch.no_grad():
            completion_result = self.gestalt_completer(partial_pattern)
        simplex = {
            "id": f"simplex_{len(self.simplexes):06d}",
            "vertex_ids": vertex_ids,
            "simplex_type": simplex_type,
            "coherence": float(avg_similarity),
            "coherence_variance": float(coherence_variance),
            "gestalt_completion": completion_result,
            "created_at": self._current_timestamp(),
            "edges": len(similarities),
        }
        self.simplexes.append(simplex)
        self.coherence_history.append(simplex["coherence"])
        self.completion_history.append(completion_result["completion_confidence"].item())
        return simplex

    def evolve_simplex(self, simplex_id: str, time_steps: int = 10, dt: float = 0.1) -> Dict:
        simplex = next((s for s in self.simplexes if s["id"] == simplex_id), None)
        if simplex is None:
            raise ValueError(f"Simplex {simplex_id} not found")
        vertices = [self.vertices[vid] for vid in simplex["vertex_ids"]]
        embeddings = torch.stack([v.unified_embedding for v in vertices])
        from sklearn.decomposition import PCA

        pca = PCA(n_components=3)
        embeddings_np = embeddings.numpy()
        spatial_coords = pca.fit_transform(embeddings_np)
        evolution_history = []
        for step in range(time_steps):
            t = step * dt
            coords = np.zeros((len(vertices), 4))
            coords[:, :3] = spatial_coords
            coords[:, 3] = t
            coords_tensor = torch.tensor(coords, dtype=torch.float32)
            with torch.enable_grad():
                pde_result = self.continuum_pde(coords_tensor)
                pde_residual = self.continuum_pde.compute_pde_residual(coords_tensor)
            for i, vertex_id in enumerate(simplex["vertex_ids"]):
                vertex = self.vertices[vertex_id]
                density = pde_result["density"][i].item()
                phase = pde_result["phase"][i].item()
                rotation = torch.tensor([[np.cos(phase), -np.sin(phase)], [np.sin(phase), np.cos(phase)]])
                # vertex.intentional_vector = rotation @ vertex.intentional_vector # simplified
                vertex.embodied_vector *= density
            evolution_history.append(
                {
                    "time": t,
                    "average_density": pde_result["density"].mean().item(),
                    "average_phase": pde_result["phase"].mean().item(),
                    "residual_magnitude": pde_residual["residual_magnitude"].mean().item(),
                    "coherence": simplex["coherence"],
                }
            )
        return {
            "simplex_id": simplex_id,
            "evolution_steps": time_steps,
            "dt": dt,
            "history": evolution_history,
            "final_coherence": evolution_history[-1]["coherence"] if evolution_history else 0.0,
        }

    def find_gestalt_completions(self, partial_pattern: torch.Tensor, threshold: float = 0.7) -> List[Dict]:
        completions = []
        with torch.no_grad():
            pattern_completion = self.gestalt_completer(partial_pattern)
            pattern_embedding = pattern_completion["latent_z"]
        for simplex in self.simplexes:
            simplex_vertices = [self.vertices[vid] for vid in simplex["vertex_ids"]]
            simplex_embedding = torch.stack([v.unified_embedding for v in simplex_vertices])
            simplex_center = torch.mean(simplex_embedding, dim=0)
            similarity = F.cosine_similarity(pattern_embedding, simplex_center.unsqueeze(0)).item()
            if similarity > threshold:
                completions.append(
                    {
                        "simplex": simplex,
                        "similarity": similarity,
                        "completion_confidence": pattern_completion["completion_confidence"].item(),
                        "gestalt_type": self._classify_gestalt_type(simplex),
                    }
                )
        return sorted(completions, key=lambda x: x["similarity"], reverse=True)

    def _classify_gestalt_type(self, simplex: Dict) -> str:
        coherence = simplex["coherence"]
        variance = simplex["coherence_variance"]
        if coherence > 0.8 and variance < 0.1:
            return "HOLISTIC_INTEGRATION"
        elif coherence > 0.6 and variance < 0.2:
            return "STRUCTURAL_COMPLETION"
        elif coherence > 0.4:
            return "PARTIAL_INSIGHT"
        else:
            return "EMERGENT_PATTERN"

    def _current_timestamp(self) -> str:
        from datetime import datetime

        return datetime.utcnow().isoformat() + "Z"

    def to_json(self, filename: str):
        data = {
            "vertices": {
                vid: {
                    "type": v.type.value,
                    "intentional_shape": list(v.intentional_vector.shape),
                    "embodied_shape": list(v.embodied_vector.shape),
                    "geometric_shape": list(v.geometric_vector.shape),
                }
                for vid, v in self.vertices.items()
            },
            "simplexes": self.simplexes,
            "graph_stats": {
                "n_vertices": len(self.vertices),
                "n_simplexes": len(self.simplexes),
                "average_coherence": np.mean(self.coherence_history) if self.coherence_history else 0.0,
                "average_completion": np.mean(self.completion_history) if self.completion_history else 0.0,
            },
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2, default=str)


def create_gestalt_workflow(config: Optional[Dict] = None):
    if config is None:
        config = {"embedding_dim": 512, "evolution_steps": 20, "dt": 0.05}
    print("🚀 INITIALIZING GESTALT ARTIFICIAL WORKFLOW")
    kernel = OntologicalGraphKernel(embedding_dim=config.get("embedding_dim", 512))
    foundational_types = [
        ("consciousness_intentional", OntologicalType.INTENTIONAL),
        ("biological_embodied", OntologicalType.EMBODIED),
        ("mathematical_formal", OntologicalType.MATHEMATICAL),
    ]
    for vertex_id, vtype in foundational_types:
        kernel.add_vertex(vertex_id, vtype)
    initial_simplex = kernel.form_simplex(
        ["consciousness_intentional", "biological_embodied", "mathematical_formal"], simplex_type="foundational_triune"
    )
    evolution = kernel.evolve_simplex(
        initial_simplex["id"], time_steps=config.get("evolution_steps", 20), dt=config.get("dt", 0.05)
    )
    return kernel, evolution


if __name__ == "__main__":
    kernel, evolution = create_gestalt_workflow()
    print(f"✅ Workflow complete. Simplex coherence: {kernel.simplexes[0]['coherence']:.3f}")
