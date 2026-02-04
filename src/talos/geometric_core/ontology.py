from __future__ import annotations

from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    COMMODITY = "commodity"
    EQUITY = "equity"
    DIGITAL_NATIVE = "digital_native"


class InstitutionalAttributes(BaseModel):
    has_voting_rights: bool = False
    asset_class: AssetClass = AssetClass.DIGITAL_NATIVE


class OntologyNode(BaseModel):
    id: str
    label: Optional[str] = None
    attrs: Dict[str, str] = Field(default_factory=dict)
    institutional: Optional[InstitutionalAttributes] = None


class OntologyGraph(BaseModel):
    nodes: Dict[str, OntologyNode] = Field(default_factory=dict)

    def add_node(self, node: OntologyNode):
        self.nodes[node.id] = node
