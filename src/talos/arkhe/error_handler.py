"""
Arkhe(n) Error Handler.
Provides robust error handling and logging for the Arkhe framework.
"""

from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable

# Configure logging
logging.basicConfig(
    filename="arkhe_core.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def safe_operation(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to wrap critical operations in a try-except block.
    Logs errors and re-raises them.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            # In a production environment, this could trigger a recovery protocol.
            raise

    return wrapper


@safe_operation
def fetch_node_data(node_id: int | str) -> dict[str, float]:
    """
    Simulates fetching data from a remote node.
    """
    if node_id == 42:
        raise ConnectionError("Node 42 did not respond to handshake")
    return {"C": 0.95, "F": 0.05}


@safe_operation
def write_ledger(entry: str) -> None:
    """
    Simulates writing an entry to the system ledger.
    """
    # In a real scenario, this would persist to a database or distributed ledger.
    with open("arkhe_ledger.txt", "a", encoding="utf-8") as f:
        f.write(entry + "\n")
