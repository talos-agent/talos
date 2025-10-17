#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AO Research Controller – versão 1.0.0
Implementação mínima e reproduzível de um controlador adaptativo
baseado em Lyapunov, com exportação de resultados para IPFS.
"""

from __future__ import annotations

import dataclasses
import json
import logging
import time
from pathlib import Path
from typing import Callable, Tuple

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Logging (reprodutível – nível INFO por padrão)
# --------------------------------------------------------------------------- #
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
logger.handlers.clear()
logger.addHandler(handler)

# --------------------------------------------------------------------------- #
# Dataclasses – configuração e resultados
# --------------------------------------------------------------------------- #
@dataclasses.dataclass
class TrialConfig:
    """Parâmetros fixos de um experimento."""

    # Temporal
    duration: float = 8.0          # [s]
    dt: float = 0.01               # passo de integração [s]

    # Referência (primeira ordem)
    ref_gain: float = 1.0
    ref_tc: float = 0.5

    # Planta demo (segundo ordem)
    plant_wn: float = 2.0          # frequência natural [rad/s]
    plant_zeta: float = 0.7        # amortecimento

    # Lei adaptativa (Lyapunov)
    gamma: float = 20.0            # taxa de adaptação
    sigma: float = 0.01            # termo de vazamento (regularizador)

    # Segurança
    max_control: float = 5.0       # saturação do atuador
    max_error: float = 10.0        # aborta se |e| > limite

    # Semente para reproducibilidade
    rng_seed: int = 42

    # Pasta de saída (relativa ao diretório de execução)
    out_dir: Path = Path("./results")

    # Flags
    verbose: bool = False


@dataclasses.dataclass
class TrialResult:
    """Armazena tudo que foi medido."""

    time: np.ndarray
    error: np.ndarray
    control: np.ndarray
    plant_state: np.ndarray   # [x, xdot]
    theta: np.ndarray          # parâmetros adaptativos estimados

    # Metadados (para o JSON)
    config: dict
    ipfs_cid: str | None = None


# --------------------------------------------------------------------------- #
# Funções auxiliares
# --------------------------------------------------------------------------- #
def reference_signal(t: float, cfg: TrialConfig) -> float:
    """Primeira ordem: y_r(t) = K (1 - e^{-t/τ})"""
    return cfg.ref_gain * (1.0 - math.exp(-t / cfg.ref_tc))


def plant_dynamics(x: np.ndarray, u: float, cfg: TrialConfig) -> np.ndarray:
    """
    Segunda‑ordem linear:  x'' + 2ζωₙ x' + ωₙ² x = u
    Estado x = [position, velocity]
    """
    pos, vel = x
    acc = u - 2 * cfg.plant_zeta * cfg.plant_wn * vel - (cfg.plant_wn ** 2) * pos
    return np.array([vel, acc])


def lyapunov_adaptive_law(e: float, phi: np.ndarray, theta: np.ndarray,
                         cfg: TrialConfig) -> Tuple[float, np.ndarray]:
    """
    Controle u = θᵀ φ
    Atualiza θ via:  \dotθ = -γ φ e - σ θ   (Lyapunov‑based)
    phi = [x, xdot, r]  – regressor
    """
    # Atualiza parâmetros
    dtheta = -cfg.gamma * phi * e - cfg.sigma * theta
    theta_new = theta + dtheta * cfg.dt

    # Controle saturado (antes da saturação, calcula u)
    u = np.dot(theta_new, phi)

    # Saturação física
    if abs(u) > cfg.max_control:
        u = np.sign(u) * cfg.max_control

    return u, theta_new


# --------------------------------------------------------------------------- #
# Runner – executa o experimento inteiro
# --------------------------------------------------------------------------- #
def run_trial(cfg: TrialConfig) -> TrialResult:
    """Executa a simulação completa e devolve todos os vetores."""
    # Preparação
    np.random.seed(cfg.rng_seed)
    steps = int(cfg.duration / cfg.dt) + 1
    t_vec = np.linspace(0.0, cfg.duration, steps)

    # Vetores para gravação
    e_vec = np.empty(steps)
    u_vec = np.empty(steps)
    x_vec = np.empty((steps, 2))
    th_vec = np.empty((steps, 3))  # θ ∈ ℝ³ (x, xdot, r)

    # Condições iniciais
    x = np.array([0.0, 0.0])          # planta: posição e velocidade
    theta = np.zeros(3)              # parâmetros iniciais (todos zero)

    for i, t in enumerate(t_vec):
        # Referência
        r = reference_signal(t, cfg)

        # Erro de rastreamento
        y = x[0]                      # saída da planta (posição)
        e = y - r
        e_vec[i] = e

        # Regresso (phi) = [x, xdot, r]
        phi = np.array([x[0], x[1], r])

        # Lei adaptativa
        u, theta = lyapunov_adaptive_law(e, phi, theta, cfg)
        u_vec[i] = u
        th_vec[i] = theta

        # Integração da planta (Euler explícito)
        x_dot = plant_dynamics(x, u, cfg)
        x = x + x_dot * cfg.dt
        x_vec[i] = x

        # Segurança – aborta se algo explode
        if (abs(u) > cfg.max_control * 1.5) or (abs(e) > cfg.max_error):
            logger.warning(f"Abortando em t={t:.2f}s (segurança).")
            e_vec = e_vec[: i + 1]
            u_vec = u_vec[: i + 1]
            x_vec = x_vec[: i + 1]
            th_vec = th_vec[: i + 1]
            t_vec = t_vec[: i + 1]
            break

        if cfg.verbose and i % 100 == 0:
            logger.debug(f"t={t:.2f}s | e={e:.3f} | u={u:.3f}")

    # Monta metadados
    meta = {
        "config": dataclasses.asdict(cfg),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "seed": cfg.rng_seed,
    }

    # Salva arquivos locais (CSV + JSON) – será usado para upload IPFS
    out_path = cfg.out_dir
    out_path.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame({
        "time": t_vec,
        "reference": [reference_signal(tt, cfg) for tt in t_vec],
        "plant_pos": x_vec[:, 0],
        "plant_vel": x_vec[:, 1],
        "error": e_vec,
        "control": u_vec,
        "theta_1": th_vec[:, 0],
        "theta_2": th_vec[:, 1],
        "theta_3": th_vec[:, 2],
    })
    csv_file = out_path / "trial_data.csv"
    df.to_csv(csv_file, index=False)

    json_file = out_path / "metadata.json"
    json_file.write_text(json.dumps(meta, indent=2))

    logger.info(f"Resultados gravados em {out_path}")

    return TrialResult(
        time=t_vec,
        error=e_vec,
        control=u_vec,
        plant_state=x_vec,
        theta=th_vec,
        config=meta,
        ipfs_cid=None,   # será preenchido depois do upload
    )