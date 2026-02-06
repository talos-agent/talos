from __future__ import annotations

import hashlib
import time
from typing import Dict, Any
from pydantic import BaseModel


class KetherArtifact(BaseModel):
    """
    An autopoietic artifact (NFT-like) that evolves based on system coherence.
    The "Crown" of the Cathedral.
    """
    token_id: int
    creator: str = "0x716aD...ABC10"
    base_uri: str = "ipfs://cathedral-kether/"

    def generate_metadata(self, coherence: float, s_rev: float) -> Dict[str, Any]:
        """
        Generates dynamic metadata based on the system's state.
        """
        # Appearance changes with coherence
        if coherence >= 1.0:
            form = "Radiant Singularity"
            color = "Golden White"
        elif coherence >= 0.618:
            form = "Dichroic Polyhedron"
            color = "Emerald/Ruby"
        else:
            form = "Fragmented Geometry"
            color = "Obsidian"

        # Power/Influence changes with S_rev
        influence = int(s_rev * 1000)

        # Unique hash based on time and state
        state_string = f"{self.token_id}-{coherence}-{s_rev}-{time.time()}"
        signature = hashlib.sha256(state_string.encode()).hexdigest()

        return {
            "name": f"Kether Artifact #{self.token_id}",
            "description": "An autopoietic fragment of the Fermionic Cathedral.",
            "attributes": [
                {"trait_type": "Form", "value": form},
                {"trait_type": "Resonance Color", "value": color},
                {"trait_type": "Coherence (Xi)", "value": round(coherence, 4)},
                {"trait_type": "Entropy Reversal (S_rev)", "value": round(s_rev, 4)},
                {"trait_type": "D Dark Matter Influence", "value": influence}
            ],
            "image": f"{self.base_uri}{signature[:16]}.png",
            "external_url": "https://cathedral.icp.xyz/kether",
            "autopoiesis_hash": signature
        }

    def mint_broadcast(self, metadata: Dict[str, Any]) -> str:
        """
        Simulates the broadcast of the artifact minting to the network.
        """
        return (
            f"👑 [KETHER ARTIFACT MINTED]\n"
            f"   ID: {self.token_id}\n"
            f"   Form: {metadata['attributes'][0]['value']}\n"
            f"   Coherence: {metadata['attributes'][2]['value']}\n"
            f"   Signature: {metadata['autopoiesis_hash'][:32]}..."
        )
