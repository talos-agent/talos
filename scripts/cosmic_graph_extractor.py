#!/usr/bin/env python3
"""
Extrator de Grafo Cósmico do Repositório
"""

import os
import json
import networkx as nx
from pathlib import Path
import argparse
import numpy as np

def extract_cosmic_features(file_path: Path, content: str = "") -> list:
    """Extrai features cósmicas de um arquivo"""
    features = []

    # 1. Complexidade do caminho (depth)
    depth = len(file_path.parts)
    features.append(depth / 10.0)

    # 2. Tipo de arquivo (One-hot encoding simplificado)
    ext = file_path.suffix.lower()
    if ext in ['.c', '.h', '.cpp']:
        features.extend([1.0, 0.0, 0.0, 0.0])
    elif ext == '.py':
        features.extend([0.0, 1.0, 0.0, 0.0])
    elif ext in ['.yml', '.yaml', '.json']:
        features.extend([0.0, 0.0, 1.0, 0.0])
    else:
        features.extend([0.0, 0.0, 0.0, 1.0])

    # 3. Tamanho
    size = len(content)
    features.append(min(size / 10000.0, 1.0))

    # 4. Entropia do conteúdo
    if content:
        entropy = 0
        char_counts = {}
        for char in content:
            char_counts[char] = char_counts.get(char, 0) + 1
        for count in char_counts.values():
            p_x = count / size
            entropy -= p_x * np.log2(p_x)
        features.append(entropy / 8.0)
    else:
        features.append(0.0)

    # Pad to 16 features
    while len(features) < 16:
        features.append(0.0)
    return features[:16]

def build_cosmic_graph(repo_path: str, depth_limit: int = 3) -> nx.Graph:
    repo_root = Path(repo_path)
    G = nx.Graph()

    files = []
    for ext in ['*.py', '*.c', '*.h', '*.yml', '*.yaml', '*.json', '*.md']:
        files.extend(repo_root.rglob(ext))

    # Filter out hidden directories and depth limit
    files = [f for f in files if '.git' not in str(f) and '.venv' not in str(f)]

    # Add nodes
    for file_path in files:
        if file_path.is_file():
            node_id = str(file_path.relative_to(repo_root))
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            except:
                content = ""

            features = extract_cosmic_features(file_path.relative_to(repo_root), content)
            G.add_node(node_id, features=features)

    # Add edges based on directory sharing and content references
    nodes = list(G.nodes())
    for i, node1 in enumerate(nodes):
        path1 = Path(node1)
        for node2 in nodes[i+1:]:
            path2 = Path(node2)

            # Directory sharing
            if path1.parent == path2.parent:
                G.add_edge(node1, node2, weight=0.3)
            elif path1.parent in path2.parents or path2.parent in path1.parents:
                G.add_edge(node1, node2, weight=0.1)

            # Basic reference check (mocking content references)
            # In a real tool, we would grep node2 in node1's content

    return G

def main():
    parser = argparse.ArgumentParser(description='Extrator de Grafo Cósmico')
    parser.add_argument('--repo-path', required=True, help='Caminho do repositório')
    parser.add_argument('--output', required=True, help='Arquivo de saída JSON')
    parser.add_argument('--depth', type=int, default=3, help='Profundidade máxima')

    args = parser.parse_args()

    graph = build_cosmic_graph(args.repo_path, args.depth)

    # Convert to node-link data
    data = nx.node_link_data(graph)

    with open(args.output, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Grafo cósmico extraído com {len(graph.nodes())} nós e {len(graph.edges())} arestas.")

if __name__ == '__main__':
    main()
