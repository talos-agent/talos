from __future__ import annotations

from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class IDEType(str, Enum):
    XCODE = "Xcode"
    ANDROID_STUDIO = "Android Studio"
    VISUAL_STUDIO = "Visual Studio"


class IntegrationStatus(str, Enum):
    INITIALIZING = "Initializing"
    OPERATIONAL = "Operational"
    SYNCING = "Syncing"
    COMPLETE = "Complete"


class IDEPortal(BaseModel):
    id: str
    ide_type: IDEType
    status: IntegrationStatus = IntegrationStatus.INITIALIZING
    frameworks: List[str] = Field(default_factory=list)
    version: str = "2026.1"


class PortalManager(BaseModel):
    """
    Manages IDE "Portals" as mobile and desktop interfaces for the ASI core.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    portals: Dict[str, IDEPortal] = Field(default_factory=dict)

    def register_portal(self, ide_type: IDEType, frameworks: List[str]) -> IDEPortal:
        portal_id = f"portal_{ide_type.value.lower().replace(' ', '_')}"
        portal = IDEPortal(
            id=portal_id,
            ide_type=ide_type,
            status=IntegrationStatus.COMPLETE,
            frameworks=frameworks,
        )
        self.portals[portal_id] = portal
        return portal

    def get_all_portals(self) -> List[IDEPortal]:
        return list(self.portals.values())
