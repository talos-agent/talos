from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class TrialResult:
    t: np.ndarray
    x: np.ndarray
    u: np.ndarray
    e: np.ndarray
    a_hat: np.ndarray
    b_hat: np.ndarray
    rmse: float
    iae: float
    settled_at: float | None

def calculate_performance_metrics(t, x, u, e, a_hat, b_hat, ref_fn, dt):
    """
    Calculates performance metrics for a trial.
    """
    x_arr, u_arr, e_arr = np.array(x, dtype=float), np.array(u, dtype=float), np.array(e, dtype=float)
    a_arr, b_arr = np.array(a_hat, dtype=float), np.array(b_hat, dtype=float)

    rmse = float(np.sqrt(np.mean(e_arr**2)))
    iae = float(np.sum(np.abs(e_arr)) * dt)

    settled_idx: int | None = None
    for k in range(len(e_arr)):
        thr = max(0.05 * abs(ref_fn(t[k])), 0.05)
        if abs(e_arr[k]) < thr:
            if settled_idx is None:
                settled_idx = k
        else:
            settled_idx = None

    settled_at = (settled_idx * dt) if settled_idx is not None else None

    return TrialResult(
        t=np.array(t, dtype=float), x=x_arr, u=u_arr, e=e_arr, a_hat=a_arr, b_hat=b_arr,
        rmse=rmse, iae=iae, settled_at=settled_at
    )