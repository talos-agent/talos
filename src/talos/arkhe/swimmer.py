from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


class FlagellarSwimmer:
    """
    Simulação de um microswimmer com flagelo descrito por uma onda senoidal.
    """

    def __init__(
        self,
        L: float = 10.0,
        A: float = 1.0,
        wavelength: float = 5.0,
        omega: float = 2 * np.pi,
        N: int = 100,
        C_par: float = 1.0,
        C_perp: float = 2.0,
        dt: float = 0.01,
    ):
        self.L = L
        self.A = A
        self.k = 2 * np.pi / wavelength
        self.omega = omega
        self.N = N  # número de segmentos
        self.C_par = C_par
        self.C_perp = C_perp
        self.dt = dt

        # coordenada ao longo do flagelo (0 a L)
        self.s = np.linspace(0, L, N)
        self.ds = self.s[1] - self.s[0]

        # posição inicial do flagelo (no referencial do corpo)
        self.x = np.zeros(N)
        self.y = np.zeros(N)
        self.t: float = 0.0
        self.update_shape(t=0.0)

        # posição do corpo (cabeça) no referencial inercial
        self.body_x = 0.0
        self.body_y = 0.0

        # velocidades
        self.vx = 0.0
        self.vy = 0.0

        self.x_world = self.body_x + self.x
        self.y_world = self.body_y + self.y

    def update_shape(self, t: float) -> None:
        """Atualiza a forma do flagelo no referencial do corpo."""
        # Onda viajante para a direita
        self.y = self.A * np.sin(self.k * self.s - self.omega * t)
        self.x = self.s  # aproximação inextensível (simples)

    def compute_velocity(self) -> tuple[float, float]:
        """
        Calcula a velocidade do corpo baseado na forma e na velocidade de
        deformação do flagelo, usando RFT.
        """
        # velocidade de cada segmento no referencial do corpo
        dy_dt = -self.A * self.omega * np.cos(self.k * self.s - self.omega * self.t)
        dx_dt = np.zeros_like(dy_dt)  # o flagelo não se alonga

        # derivadas espaciais para a inclinação
        dy_ds = self.A * self.k * np.cos(self.k * self.s - self.omega * self.t)
        # a norma do vetor tangente (deve ser constante)
        norm = np.sqrt(1 + dy_ds**2)
        # cosseno e seno do ângulo local
        cos_psi = 1 / norm
        sin_psi = dy_ds / norm

        # velocidades tangencial e normal no referencial do segmento
        v_tang = dx_dt * cos_psi + dy_dt * sin_psi
        v_norm = -dx_dt * sin_psi + dy_dt * cos_psi

        # forças viscosas por unidade de comprimento (RFT)
        f_tang = -self.C_par * v_tang
        f_norm = -self.C_perp * v_norm

        # força total no flagelo (integrando)
        fx_total = np.sum((f_tang * cos_psi - f_norm * sin_psi)) * self.ds
        fy_total = np.sum((f_tang * sin_psi + f_norm * cos_psi)) * self.ds

        # o corpo (cabeça) sofre arrasto viscoso
        c_body = 1.0  # ajustável
        vx_body = fx_total / c_body
        vy_body = fy_total / c_body

        return float(vx_body), float(vy_body)

    def step(self, t: float) -> None:
        self.t = t
        self.update_shape(t)
        vx, vy = self.compute_velocity()
        self.body_x += vx * self.dt
        self.body_y += vy * self.dt
        # a forma do flagelo no referencial inercial
        self.x_world = self.body_x + self.x
        self.y_world = self.body_y + self.y

    def run(
        self, t_max: float, save_animation: bool = False
    ) -> tuple[np.ndarray, np.ndarray, list[tuple[np.ndarray, np.ndarray]]]:
        self.t = 0.0
        self.body_x = 0.0
        self.body_y = 0.0
        history_x = []
        history_y = []
        frames = []
        for _ in range(int(t_max / self.dt)):
            self.step(self.t)
            history_x.append(self.body_x)
            history_y.append(self.body_y)
            if save_animation:
                frames.append((self.x_world.copy(), self.y_world.copy()))
            self.t += self.dt
        return np.array(history_x), np.array(history_y), frames

    def animate(
        self, frames: list[tuple[np.ndarray, np.ndarray]], output_path: str = "swimmer.mp4"
    ) -> FuncAnimation:
        """Gera uma animação da simulação."""
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_xlim(-2, self.L + 10)
        ax.set_ylim(-3, 3)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(alpha=0.3)
        (line,) = ax.plot([], [], "k-", lw=2)
        (head,) = ax.plot([], [], "ro", markersize=8)
        (tail,) = ax.plot([], [], "ko", markersize=3)

        def init():
            line.set_data([], [])
            head.set_data([], [])
            tail.set_data([], [])
            return line, head, tail

        def update(i):
            x_f, y_f = frames[i]
            line.set_data(x_f, y_f)
            head.set_data([x_f[0]], [y_f[0]])
            tail.set_data([x_f[-1]], [y_f[-1]])
            return line, head, tail

        ani = FuncAnimation(fig, update, frames=len(frames), init_func=init, blit=True)
        if output_path.endswith(".mp4"):
            ani.save(output_path, writer="ffmpeg", fps=50)
        plt.close()
        return ani
