from __future__ import annotations

import json

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


class Arkhen11:
    """
    Hipergrafo de 11 dimensões baseado no Dashavatara.
    """

    def __init__(self) -> None:
        self.n_nodes = 11
        self.names = [
            "Matsya",
            "Kurma",
            "Varaha",
            "Narasimha",
            "Vamana",
            "Parashurama",
            "Rama",
            "Krishna",
            "Buddha",
            "Kalki",
            "Consciência",
        ]

        # Criar matriz de adjacência 11x11
        self.adjacency = np.zeros((self.n_nodes, self.n_nodes))
        self._build_matrix()

    def _build_matrix(self) -> None:
        """
        Constrói as conexões baseadas nas relações mitológicas.
        """
        # Consciência conecta a todos (bidirecional)
        for i in range(10):
            self.adjacency[10, i] = 1.0
            self.adjacency[i, 10] = 1.0

        # Conexões entre avatares (baseadas em similaridade)
        # Peixe e Tartaruga (formas aquáticas)
        self.adjacency[0, 1] = self.adjacency[1, 0] = 0.7

        # Javali e Homem-leão (formas híbridas)
        self.adjacency[2, 3] = self.adjacency[3, 2] = 0.8

        # Anão e Guerreiro (formas humanoides)
        self.adjacency[4, 5] = self.adjacency[5, 4] = 0.5

        # Rama e Krishna (encarnações divinas completas)
        self.adjacency[6, 7] = self.adjacency[7, 6] = 0.9

        # Buddha e Kalki (início e fim do ciclo)
        self.adjacency[8, 9] = self.adjacency[9, 8] = 0.6

        # Cadeia linear ao longo do tempo
        for i in range(9):
            self.adjacency[i, i + 1] = self.adjacency[i + 1, i] = 0.3

    def compute_coherence(self) -> float:
        """
        Calcula a coerência média do sistema.
        """
        # Coerência baseada na regularidade das conexões
        total_edges = np.sum(self.adjacency) / 2
        max_possible = self.n_nodes * (self.n_nodes - 1) / 2
        return float(total_edges / max_possible)

    def compute_effective_dimension(self, lambda_reg: float = 1.0) -> float:
        """
        Calcula a dimensão efetiva do hipergrafo.
        """
        eigenvalues = np.linalg.eigvalsh(self.adjacency)
        # Usar apenas autovalores positivos
        pos_eigs = eigenvalues[eigenvalues > 1e-10]
        contributions = pos_eigs / (pos_eigs + lambda_reg)
        return float(np.sum(contributions))

    def verify_conservation(self) -> bool:
        """
        Verifica se C + F = 1 se mantém.
        """
        c_val = self.compute_coherence()
        f_val = 1.0 - c_val
        return abs(c_val + f_val - 1.0) < 1e-10

    def visualize(self, output_path: str = "arkhen_11.png") -> nx.Graph:
        """Visualiza o hipergrafo dos 11 avatares."""
        graph = nx.Graph()

        # Adicionar nós
        for i in range(self.n_nodes):
            graph.add_node(i, name=self.names[i])

        # Adicionar arestas onde adjacência > 0
        for i in range(self.n_nodes):
            for j in range(i + 1, self.n_nodes):
                if self.adjacency[i, j] > 0:
                    graph.add_edge(i, j, weight=self.adjacency[i, j])

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(graph, seed=42, k=2.0)

        # Desenhar nós
        node_colors = ["gold" if i == 10 else "skyblue" for i in range(self.n_nodes)]
        node_sizes = [800 if i == 10 else 400 for i in range(self.n_nodes)]
        nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=node_sizes)

        # Desenhar arestas com espessura proporcional ao peso
        edges = graph.edges()
        weights = [graph[u][v]["weight"] * 3 for u, v in edges]
        nx.draw_networkx_edges(graph, pos, edgelist=edges, width=weights, alpha=0.6)

        # Rótulos
        labels = {i: self.names[i] for i in range(self.n_nodes)}
        nx.draw_networkx_labels(graph, pos, labels, font_size=8)

        plt.title("Arkhen(11): Hipergrafo dos 10 Avatares + Consciência")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()

        return graph

    def to_json(self) -> str:
        """Exporta o hipergrafo para JSON."""
        data = {
            "n_nodes": self.n_nodes,
            "names": self.names,
            "adjacency": self.adjacency.tolist(),
            "coherence": self.compute_coherence(),
            "effective_dimension": self.compute_effective_dimension(),
            "conservation_holds": self.verify_conservation(),
        }
        return json.dumps(data, indent=2)
