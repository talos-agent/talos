from __future__ import annotations

import numpy as np
from typing import Tuple
from .schema import Vertex, ContextDomain, Simplex
from .semantic_network import UnifiedSemanticNetwork

def create_forest_simplex() -> Tuple[UnifiedSemanticNetwork, Simplex]:
    """
    Creates the first operational simplex: ("Floresta Amazônica", "Constituição Brasileira Artigo 225", "Assembleia dos Povos da Floresta").
    """
    net = UnifiedSemanticNetwork()

    # 1. SYLVA: O Ecossistema
    forest_vertex = Vertex(
        id="amazon_forest",
        name="Floresta Amazônica",
        domain=ContextDomain.ECOLOGY,
        position=np.array([0.2, 0.8, 0.1]),
        attributes={"health": 0.7, "biodiversity_index": 0.9}
    )
    net.add_concept(forest_vertex)

    # 2. CONCORDIA: A Lei
    law_vertex = Vertex(
        id="brazil_const_225",
        name="Constituição Brasileira Artigo 225",
        domain=ContextDomain.LAW,
        position=np.array([0.7, 0.3, 0.9]),
        attributes={"type": "fundamental_right", "scope": "environmental"}
    )
    net.add_concept(law_vertex)

    # 3. SYNESIS: A Assembleia
    assembly_vertex = Vertex(
        id="forest_peoples_assembly",
        name="Assembleia dos Povos da Floresta",
        domain=ContextDomain.DELIBERATION,
        position=np.array([0.5, 0.5, 0.5]),
        attributes={"participants": "Indigenous leaders, local communities", "legitimacy": 0.95}
    )
    net.add_concept(assembly_vertex)

    # 4. Project KEEL: Axiomatic Vertices
    un_charter = Vertex(
        id="un_charter",
        name="UN Charter",
        domain=ContextDomain.LAW,
        position=np.array([1.0, 1.0, 1.0]),
        attributes={"type": "axiomatic", "authority": "Global"}
    )
    net.add_concept(un_charter)

    human_rights = Vertex(
        id="human_rights",
        name="Universal Declaration of Human Rights",
        domain=ContextDomain.LAW,
        position=np.array([0.9, 0.9, 0.9]),
        attributes={"type": "axiomatic", "authority": "Universal"}
    )
    net.add_concept(human_rights)

    # Add relations
    net.add_relation("amazon_forest", "brazil_const_225", "justifies_protection_of", weight=1.0)
    net.add_relation("brazil_const_225", "forest_peoples_assembly", "empowers", weight=0.8)
    net.add_relation("forest_peoples_assembly", "amazon_forest", "stewards", weight=0.9)

    # Project KEEL constraints: Axioms connect to all legal frameworks
    net.add_relation("un_charter", "brazil_const_225", "anchors", weight=1.0)
    net.add_relation("human_rights", "forest_peoples_assembly", "protects_participants", weight=1.0)

    # Form simplex
    simplex = net.form_simplex(
        id="amazon_guardianship",
        name="Guardiões da Amazônia",
        vertex_ids=["amazon_forest", "brazil_const_225", "forest_peoples_assembly"],
        semantic_type="tripartite_stewardship"
    )

    return net, simplex
