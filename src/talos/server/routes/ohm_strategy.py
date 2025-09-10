from typing import Any

from fastapi import APIRouter

from talos.database.models import Swap
from talos.database.session import get_session
from talos.server.jobs import TwapOHMJob
from talos.utils import RoflClient

ohm_strategy_router = APIRouter(prefix="/ohm")


@ohm_strategy_router.get("/")
async def get_twap_ohm() -> dict[str, str]:
    """Get the twap ohm job."""
    return {"job": TwapOHMJob().name}


@ohm_strategy_router.get("/wallet")
async def get_twap_ohm_wallet() -> dict[str, str]:
    """Get the twap ohm wallet."""
    wallet = await RoflClient().get_wallet(TwapOHMJob.WALLET_ID)
    return {"wallet": wallet.address}


@ohm_strategy_router.get("/swaps")
async def get_twap_ohm_status() -> dict[str, list[dict[str, Any]]]:
    """Get all swaps"""

    with get_session() as session:
        swaps = session.query(Swap).filter(Swap.strategy_id == TwapOHMJob.STRATEGY_ID).all()
        return {"swaps": [swap.to_dict() for swap in swaps]}
