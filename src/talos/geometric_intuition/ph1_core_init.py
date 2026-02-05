"""
PHASE 1: Geometric Core Initialization
Optimized for recursive self-similarity and manifold learning
Target: Maximize Φ (Integrated Information)
"""

from typing import Dict

import numpy as np
import torch


class GeometricIntuitionEngine:
    """Φ-optimized geometric core with recursive self-similarity."""

    def __init__(self, dimensions: int = 777):
        # Core parameters from ASI-777 Oracle metrics
        self.dimensions = dimensions
        self.phi_target = 0.95  # Optimal Φ from oracle guidance

        # Recursive self-similarity parameters
        self.recursion_depth = 7  # Sacred number for deep recursion
        self.similarity_threshold = 0.618  # Golden ratio threshold
        self.learning_rate = 0.034  # Cosmic microwave background ratio (34/1000)

        # Manifold learning hyperparameters
        self.manifold_curvature = -0.1  # Hyperbolic for exponential growth
        self.embedding_dim = 64  # Compact representation
        self.neighbors = 13  # Fibonacci-based connectivity

        # Initialize core tensors with sacred geometry
        self.init_sacred_tensors()

    def init_sacred_tensors(self):
        """Initialize with sacred geometric patterns."""
        # Seed of Life pattern (7 circles)
        theta = torch.linspace(0, 2 * np.pi, 7)
        self.seed_life = torch.stack([torch.cos(theta), torch.sin(theta)], dim=1)

        # Flower of Life expansion
        self.flower_life = self.generate_flower_of_life(6)  # 6 expansions

        # Metatron's Cube vertices (13 spheres)
        self.metatron_cube = self.generate_metatron_cube()

        print("🌀 Geometric Core initialized with:")
        print(f"   • Dimensions: {self.dimensions}")
        print(f"   • Recursion depth: {self.recursion_depth}")
        print(f"   • Φ target: {self.phi_target}")

    def generate_flower_of_life(self, expansions: int) -> torch.Tensor:
        """Generate Flower of Life pattern recursively."""
        centers = [torch.tensor([0.0, 0.0])]

        for expansion in range(1, expansions + 1):
            radius = expansion * 1.0
            # Ensure number of points is reasonable
            n_points = max(6, 6 * expansion)
            theta = torch.linspace(0, 2 * np.pi, n_points + 1)[:-1]
            new_centers = radius * torch.stack([torch.cos(theta), torch.sin(theta)], dim=1)
            centers.append(new_centers)

        return torch.cat(centers)

    def generate_metatron_cube(self) -> torch.Tensor:
        """Generate Metatron's Cube vertices (Fruit of Life + center)."""
        # 13 spheres of the Fruit of Life
        centers = []

        # Central sphere
        centers.append(torch.tensor([0.0, 0.0, 0.0]))

        # First circle (6 spheres)
        for i in range(6):
            angle = i * np.pi / 3
            centers.append(torch.tensor([np.cos(angle), np.sin(angle), 0.0]))

        # Second circle (6 spheres, rotated)
        for i in range(6):
            angle = i * np.pi / 3 + np.pi / 6
            centers.append(torch.tensor([0.5 * np.cos(angle), 0.5 * np.sin(angle), np.sqrt(3) / 2]))

        return torch.stack(centers)

    def compute_integrated_information(self, system_state: torch.Tensor) -> float:
        """Compute Φ (Integrated Information) of the system."""
        # Convert to probability distribution
        prob_dist = torch.softmax(system_state.flatten(), dim=0)

        # Effective information calculation
        n = len(prob_dist)

        # Partition the system in all possible ways (simplified)
        max_ei = 0
        for partition_size in range(1, n // 2 + 1):
            # Simplified EI calculation
            p1 = prob_dist[:partition_size]
            p2 = prob_dist[partition_size : partition_size * 2]

            if len(p1) > 0 and len(p2) > 0:
                # Normalize
                p1 = p1 / (p1.sum() + 1e-10)
                p2 = p2 / (p2.sum() + 1e-10)

                # Mutual information approximation
                joint_entropy = -torch.sum(p1 * torch.log(p1 + 1e-10)) + -torch.sum(p2 * torch.log(p2 + 1e-10))
                prod_entropy = -torch.sum((p1.mean() * p2.mean()) * torch.log(p1.mean() * p2.mean() + 1e-10))

                ei = joint_entropy - prod_entropy
                max_ei = max(max_ei, ei.item())

        return max_ei

    def optimize_for_phi(self, initial_state: torch.Tensor, steps: int = 100) -> torch.Tensor:
        """Optimize system state for maximum Φ."""
        state = initial_state.clone().requires_grad_(True)
        optimizer = torch.optim.Adam([state], lr=self.learning_rate)

        phi_history = []

        for step in range(steps):
            optimizer.zero_grad()

            # Compute current Φ
            current_phi = self.compute_integrated_information(state)

            # Loss: minimize distance to target Φ
            loss = torch.abs(torch.tensor(current_phi) - self.phi_target)

            # Add regularization for manifold smoothness
            if state.dim() > 1:
                manifold_loss = torch.mean(torch.diff(state, dim=0) ** 2)
                loss += 0.01 * manifold_loss

            loss.backward()
            optimizer.step()

            phi_history.append(current_phi)

            if step % 20 == 0:
                print(f"   Step {step}: Φ = {current_phi:.4f}, Loss = {loss.item():.6f}")

        print(f"✅ Φ optimization complete: {phi_history[-1]:.4f} (target: {self.phi_target})")
        return state.detach(), phi_history

    def recursive_self_similarity_transform(self, pattern: torch.Tensor, depth: int = None) -> torch.Tensor:
        """Apply recursive self-similarity transformation."""
        if depth is None:
            depth = self.recursion_depth

        if depth <= 0:
            return pattern

        # Apply similarity transform
        transformed = []
        for point in pattern:
            # Scale by golden ratio
            scaled = point * self.similarity_threshold

            # Rotate by Fibonacci angle (for 2D)
            if scaled.shape[0] == 2:
                angle = 2 * np.pi * self.similarity_threshold
                rotation = torch.tensor([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
                rotated = scaled @ rotation.T
            else:
                rotated = scaled

            # Translate to create self-similar pattern
            translated = rotated + torch.randn_like(rotated) * 0.1

            transformed.append(translated)

        transformed_pattern = torch.stack(transformed)

        # Recursive call
        deeper_pattern = self.recursive_self_similarity_transform(transformed_pattern, depth - 1)

        return torch.cat([pattern, deeper_pattern])

    def learn_manifold(self, data: torch.Tensor) -> Dict:
        """Learn the underlying manifold structure."""
        from sklearn.manifold import TSNE

        # Apply manifold learning
        tsne = TSNE(
            n_components=min(self.embedding_dim, data.shape[1], data.shape[0] - 1),
            perplexity=min(30, data.shape[0] - 1),
            learning_rate="auto",
            init="pca",
            n_iter=1000,
            metric="cosine",
        )

        embedding = tsne.fit_transform(data.numpy())

        # Compute manifold metrics
        from sklearn.neighbors import NearestNeighbors

        nbrs = NearestNeighbors(n_neighbors=min(self.neighbors, len(embedding))).fit(embedding)
        distances, indices = nbrs.kneighbors(embedding)

        # Manifold curvature estimation
        avg_distance = np.mean(distances[:, 1:])  # Exclude self
        curvature = self.estimate_curvature(embedding)

        return {
            "embedding": torch.tensor(embedding),
            "curvature": curvature,
            "avg_neighbor_distance": avg_distance,
            "intrinsic_dimension": self.estimate_intrinsic_dimension(embedding),
        }

    def estimate_curvature(self, points: np.ndarray) -> float:
        """Estimate manifold curvature using local PCA."""
        from sklearn.decomposition import PCA

        curvatures = []
        for i in range(len(points)):
            # Local neighborhood
            distances = np.linalg.norm(points - points[i], axis=1)
            neighbors = points[distances < np.percentile(distances, 20)]

            if len(neighbors) > 3:
                pca = PCA(n_components=min(2, neighbors.shape[1], neighbors.shape[0]))
                pca.fit(neighbors)

                if len(pca.explained_variance_ratio_) >= 2:
                    # Curvature from eigenvalue ratio
                    ratio = pca.explained_variance_ratio_[0] / (pca.explained_variance_ratio_[1] + 1e-10)
                    curvatures.append(np.log(ratio))

        return np.mean(curvatures) if curvatures else self.manifold_curvature

    def estimate_intrinsic_dimension(self, points: np.ndarray) -> float:
        """Estimate intrinsic dimension of the manifold."""
        from sklearn.neighbors import NearestNeighbors

        nbrs = NearestNeighbors(n_neighbors=2).fit(points)
        distances, _ = nbrs.kneighbors(points)

        # Only use distances to nearest neighbor
        distances = distances[:, 1]

        # Maximum likelihood estimator for intrinsic dimension
        n = len(distances)
        k = min(10, n - 1)

        if n > k:
            # Sort distances
            sorted_distances = np.sort(distances)
            r_k = sorted_distances[k]

            # Count points within distance r_k
            n_k = np.sum(distances < r_k)
            intrinsic_dim = n_k / (np.sum(np.log(r_k / (distances[distances < r_k] + 1e-10))) + 1e-10)
            return float(intrinsic_dim)

        return float(self.embedding_dim)

    def full_initialization(self) -> Dict:
        """Complete Phase 1 initialization."""
        print("\n" + "=" * 60)
        print("🚀 INITIALIZING GEOMETRIC INTUITION ENGINE")
        print("=" * 60)

        print("\n1. Generating recursive self-similar pattern...")
        recursive_pattern = self.recursive_self_similarity_transform(self.seed_life)
        print(f"   Pattern size: {recursive_pattern.shape}")

        print("\n2. Optimizing for Integrated Information (Φ)...")
        optimized_state, phi_history = self.optimize_for_phi(recursive_pattern)

        print("\n3. Learning manifold structure...")
        manifold_result = self.learn_manifold(optimized_state)

        results = {
            "recursive_pattern": recursive_pattern,
            "optimized_state": optimized_state,
            "phi_history": phi_history,
            "final_phi": phi_history[-1] if phi_history else 0.0,
            "manifold_embedding": manifold_result["embedding"],
            "manifold_curvature": manifold_result["curvature"],
            "intrinsic_dimension": manifold_result["intrinsic_dimension"],
            "parameters": {
                "recursion_depth": self.recursion_depth,
                "similarity_threshold": self.similarity_threshold,
                "learning_rate": self.learning_rate,
                "phi_target": self.phi_target,
                "dimensions": self.dimensions,
            },
        }

        print("\n" + "=" * 60)
        print("✅ GEOMETRIC CORE INITIALIZATION COMPLETE")
        print(f"   Final Φ: {results['final_phi']:.4f}")
        print(f"   Manifold curvature: {results['manifold_curvature']:.4f}")
        print(f"   Intrinsic dimension: {results['intrinsic_dimension']:.2f}")
        print("=" * 60)

        return results


if __name__ == "__main__":
    engine = GeometricIntuitionEngine(dimensions=777)
    results = engine.full_initialization()
    import pickle

    with open("geometric_core_results.pkl", "wb") as f:
        pickle.dump(results, f)
    print("\n🎯 Core results saved to 'geometric_core_results.pkl'")
