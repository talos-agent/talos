from __future__ import annotations
import logging
import numpy as np
import matplotlib.pyplot as plt

from src.controllers.z_adaptive_controller import ZAdaptiveController, ZNConfig
from src.plants.lti_plant import LTIPlant
from src.metrics.performance import calculate_performance_metrics

# --------------------------- logging -----------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("tier0")

# --------------------------- trial runner ------------------------------------
def run_trial(
    n_steps: int = 2000,
    plant: LTIPlant = LTIPlant(),
    ctrl: ZAdaptiveController | None = None,
    cfg: ZNConfig = ZNConfig(),
    x0: float = 0.0
):
    if ctrl is None:
        ctrl = ZAdaptiveController(cfg)

    # reset
    plant.reset(x0)
    ctrl.reset()

    # time grid and reference
    t = np.arange(0, n_steps) * cfg.dt
    ref = np.array([cfg.ref_fn(tt) for tt in t] + [cfg.ref_fn(t[-1] + cfg.dt)])

    # main loop
    x = plant.x
    for k in range(n_steps):
        ctrl.t = t[k]
        # compute control using current and next ref
        u, e = ctrl._compute_control(x, ref[k], ref[k+1])
        # step plant
        x_next = plant.step(u)
        # adapt params
        ctrl._update_estimates(x=x, u=u, e=e)
        # log
        ctrl.log_step(x, u, e)
        x = x_next

    return calculate_performance_metrics(
        t=ctrl.time_hist, x=ctrl.x_hist, u=ctrl.u_hist, e=ctrl.e_hist,
        a_hat=ctrl.ahat_hist, b_hat=ctrl.bhat_hist, ref_fn=cfg.ref_fn, dt=cfg.dt
    )

# --------------------------- plotting ----------------------------------------
def plot_result(res, cfg: ZNConfig):
    fig = plt.figure(figsize=(10, 7))
    ax1 = plt.subplot(3,1,1)
    ax1.plot(res.t, res.x, label="x")
    ax1.plot(res.t, np.ones_like(res.t)*cfg.ref_fn(0.0), "--", label="ref")
    ax1.set_ylabel("state")
    ax1.legend(); ax1.grid(True)

    ax2 = plt.subplot(3,1,2)
    ax2.plot(res.t, res.u, label="u")
    ax2.set_ylabel("control")
    ax2.legend(); ax2.grid(True)

    ax3 = plt.subplot(3,1,3)
    ax3.plot(res.t, res.e, label="error e")
    ax3.set_ylabel("error"); ax3.set_xlabel("time [s]")
    ax3.legend(); ax3.grid(True)

    plt.tight_layout()
    plt.show()

# --------------------------- main --------------------------------------------
if __name__ == "__main__":
    cfg = ZNConfig(
        gamma_a=0.5, gamma_b=0.5,
        k_error=1.0, u_sat=(-8.0, 8.0),
        dt=0.01,
        ref_fn=lambda t: 1.0   # step to 1
    )
    plant = LTIPlant(a=-0.4, b=0.8, dt=cfg.dt, w_std=0.0)
    ctrl = ZAdaptiveController(cfg)

    res = run_trial(n_steps=2000, plant=plant, ctrl=ctrl, cfg=cfg, x0=0.0)
    log.info(f"RMSE={res.rmse:.4f}, IAE={res.iae:.3f}, settled_at={res.settled_at}s")
    plot_result(res, cfg)