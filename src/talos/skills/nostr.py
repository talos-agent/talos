from __future__ import annotations

import json
import time
from typing import Any, ClassVar, Optional

from pydantic import ConfigDict

from talos.core.identity import IdentityManager
from talos.skills.base import Skill


class NostrSkill(Skill):
    """
    A skill for interacting with the Nostr protocol.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: ClassVar[str] = "nostr"
    description: ClassVar[str] = "Publish messages to the Nostr network."

    identity_manager: Optional[IdentityManager] = None

    def run(self, **kwargs: Any) -> str:
        content = kwargs.get("content", "")
        if not self.identity_manager:
            return "Error: IdentityManager not configured for Nostr."

        event = {
            "pubkey": self.identity_manager.get_nostr_key(),
            "created_at": int(time.time()),
            "kind": 1,
            "tags": [],
            "content": content,
        }
        # Simulated signature
        event["id"] = "nostr_event_id"
        event["sig"] = "nostr_signature"

        return f"Signed Nostr Note: {json.dumps(event)}"
