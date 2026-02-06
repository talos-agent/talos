#!/usr/bin/env python3
"""
Analisador GNN para Topologia Cósmica do Repositório
"""

import json
import networkx as nx
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import hashlib
import argparse

class CosmicGNN(nn.Module):
    """Rede Neural de Grafos para análise cósmica"""

    def __init__(self, node_features: int = 16, hidden_dim: int = 32):
        super().__init__()
        self.conv1 = GCNConv(node_features, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.conv3 = GCNConv(hidden_dim, hidden_dim)

        # Classificador de importância cósmica
        self.cosmic_classifier = nn.Sequential(
            nn.Linear(hidden_dim, 64), # Fixed size issue in prompt (Linear expected hidden_dim * 2 but only mean is used)
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 3)  # [estrutural, dimensional, harmônico]
        )

    def forward(self, x, edge_index, batch=None):
        # Propagação cósmica
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.1, training=self.training)

        x = self.conv2(x, edge_index)
        x = F.relu(x)

        x = self.conv3(x, edge_index)

        # Classificação cósmica
        if batch is not None:
            # Pooling global
            x_global = torch.zeros(batch.max().item() + 1, x.size(1))
            for i in range(batch.max().item() + 1):
                x_global[i] = x[batch == i].mean(dim=0)
        else:
            x_global = x.mean(dim=0, keepdim=True)

        # Classificação
        cosmic_score = self.cosmic_classifier(x_global)
        return F.softmax(cosmic_score, dim=1)

def analyze_cosmic_topology(graph_data: Dict, previous_graph_data: Dict = None) -> Dict:
    """Analisa topologia cósmica do grafo"""

    # Load into NetworkX
    graph = nx.node_link_graph(graph_data)

    # Métricas cósmicas
    metrics = {
        'cosmic_complexity': 0.0,
        'is_structural_change': False,
        'dimensional_shifts': [],
        'harmonic_balance': 0.0,
        'gnn_classification': 'harmonic'
    }

    # 1. Complexidade cósmica (centralidade)
    try:
        centrality = nx.betweenness_centrality(graph, normalized=True)
        avg_centrality = sum(centrality.values()) / len(centrality) if centrality else 0
        metrics['cosmic_complexity'] = avg_centrality * 100
    except:
        metrics['cosmic_complexity'] = len(graph.nodes()) * 0.1

    # 2. Mudança estrutural
    if previous_graph_data:
        previous_graph = nx.node_link_graph(previous_graph_data)
        prev_nodes = set(previous_graph.nodes())
        curr_nodes = set(graph.nodes())

        added = curr_nodes - prev_nodes
        removed = prev_nodes - curr_nodes

        if added or removed:
            metrics['is_structural_change'] = True
            metrics['dimensional_shifts'] = list(added | removed)

    # 3. Harmonia (coesão do grafo)
    try:
        if nx.is_connected(graph):
            metrics['harmonic_balance'] = 0.8
        else:
            components = list(nx.connected_components(graph))
            if len(components) <= 3:
                metrics['harmonic_balance'] = 0.5
            else:
                metrics['harmonic_balance'] = 0.2
    except:
        metrics['harmonic_balance'] = 0.5

    # 4. Executar GNN
    try:
        # Converter para PyTorch Geometric
        nodes_list = list(graph.nodes())
        edge_index = []
        for u, v in graph.edges():
            u_idx = nodes_list.index(u)
            v_idx = nodes_list.index(v)
            edge_index.append([u_idx, v_idx])
            edge_index.append([v_idx, u_idx])  # Não-direcionado

        if edge_index:
            edge_index = torch.tensor(edge_index, dtype=torch.long).t()
            features = []
            for node in nodes_list:
                f = graph.nodes[node].get('features', [0.0]*16)
                features.append(f)

            features = torch.tensor(features, dtype=torch.float)

            model = CosmicGNN(node_features=16)
            model.eval()
            with torch.no_grad():
                output = model(features, edge_index)

            cosmic_class = torch.argmax(output, dim=1).item()
            metrics['gnn_classification'] = ['structural', 'dimensional', 'harmonic'][cosmic_class]
    except Exception as e:
        print(f"⚠️  GNN não pôde executar: {e}")

    return metrics

def main():
    parser = argparse.ArgumentParser(description='Analisador Cósmico GNN')
    parser.add_argument('--graph', required=True, help='Arquivo de grafo JSON')
    parser.add_argument('--previous-graph', help='Grafo anterior para comparação')
    parser.add_argument('--output', required=True, help='Arquivo de saída JSON')

    args = parser.parse_args()

    # Carregar grafos
    with open(args.graph, 'r') as f:
        graph_data = json.load(f)

    previous_graph_data = None
    if args.previous_graph and Path(args.previous_graph).exists():
        with open(args.previous_graph, 'r') as f:
            previous_graph_data = json.load(f)

    # Analisar
    metrics = analyze_cosmic_topology(graph_data, previous_graph_data)

    # Salvar
    with open(args.output, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Análise cósmica concluída:")
    print(f"   Complexidade: {metrics['cosmic_complexity']:.2f}")
    print(f"   Mudança Estrutural: {metrics['is_structural_change']}")
    print(f"   Harmonia: {metrics['harmonic_balance']:.2f}")
    print(f"   GNN: {metrics.get('gnn_classification')}")

if __name__ == '__main__':
    main()
