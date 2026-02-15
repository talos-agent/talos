"""
Parametric Flagellar Propulsion simulation.
Models microswimmers using Resistive Force Theory (RFT).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D


class FlagellarSwimmer:
    """
    Simulation of a microswimmer with a flagellum described by a sine wave.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        length: float = 10.0,
        amplitude: float = 1.0,
        wavelength: float = 5.0,
        omega: float = 2 * np.pi,
        num_segments: int = 100,
        c_par: float = 1.0,
        c_perp: float = 2.0,
        dt: float = 0.01,
    ):
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        self.length = length
        self.amplitude = amplitude
        self.k_num = 2 * np.pi / wavelength
        self.omega = omega
        self.num_segments = num_segments
        self.c_par = c_par
        self.c_perp = c_perp
        self.dt = dt

        # Coordinate along the flagellum
        self.s_coord = np.linspace(0, length, num_segments)
        self.ds_step = self.s_coord[1] - self.s_coord[0]

        # Flagellum position in body frame
        self.x_pos = np.zeros(num_segments)
        self.y_pos = np.zeros(num_segments)
        self.time: float = 0.0
        self.update_shape(t=0.0)

        # Body position in world frame
        self.body_x = 0.0
        self.body_y = 0.0

        self.x_world = self.body_x + self.x_pos
        self.y_world = self.body_y + self.y_pos

    def update_shape(self, t: float) -> None:
        """Updates the flagellum shape in the body reference frame."""
        self.y_pos = self.amplitude * np.sin(self.k_num * self.s_coord - self.omega * t)
        self.x_pos = self.s_coord

    def compute_velocity(self) -> tuple[float, float]:
        """
        Calculates body velocity using Resistive Force Theory (RFT).
        """
        # pylint: disable=too-many-locals
        # Temporal and spatial derivatives
        dy_dt = -self.amplitude * self.omega * np.cos(
            self.k_num * self.s_coord - self.omega * self.time
        )
        dx_dt = np.zeros_like(dy_dt)

        dy_ds = self.amplitude * self.k_num * np.cos(
            self.k_num * self.s_coord - self.omega * self.time
        )
        norm = np.sqrt(1 + dy_ds**2)
        cos_psi = 1 / norm
        sin_psi = dy_ds / norm

        # Local velocities
        v_tang = dx_dt * cos_psi + dy_dt * sin_psi
        v_norm = -dx_dt * sin_psi + dy_dt * cos_psi

        # Viscous forces per unit length
        f_tang = -self.c_par * v_tang
        f_norm = -self.c_perp * v_norm

        # Total force on flagellum
        fx_total = np.sum((f_tang * cos_psi - f_norm * sin_psi)) * self.ds_step
        fy_total = np.sum((f_tang * sin_psi + f_norm * cos_psi)) * self.ds_step

        # Body drag approximation
        c_body = 1.0
        vx_body = fx_total / c_body
        vy_body = fy_total / c_body

        return float(vx_body), float(vy_body)

    def step(self, t: float) -> None:
        """Performs a single simulation step."""
        self.time = t
        self.update_shape(t)
        vx, vy = self.compute_velocity()
        self.body_x += vx * self.dt
        self.body_y += vy * self.dt
        self.x_world = self.body_x + self.x_pos
        self.y_world = self.body_y + self.y_pos

    def run(
        self, t_max: float, save_animation: bool = False
    ) -> tuple[np.ndarray, np.ndarray, list[tuple[np.ndarray, np.ndarray]]]:
        """
        Runs the simulation for a given time.
        """
        self.time = 0.0
        self.body_x = 0.0
        self.body_y = 0.0
        history_x, history_y, frames = [], [], []
        for _ in range(int(t_max / self.dt)):
            self.step(self.time)
            history_x.append(self.body_x)
            history_y.append(self.body_y)
            if save_animation:
                frames.append((self.x_world.copy(), self.y_world.copy()))
            self.time += self.dt
        return np.array(history_x), np.array(history_y), frames

    def animate(
        self, frames: list[tuple[np.ndarray, np.ndarray]], output_path: str = "swimmer.mp4"
    ) -> FuncAnimation:
        """Generates an animation of the simulation."""
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_xlim(-2, self.length + 10)
        ax.set_ylim(-3, 3)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(alpha=0.3)
        (line,) = ax.plot([], [], "k-", lw=2)
        (head,) = ax.plot([], [], "ro", markersize=8)
        (tail,) = ax.plot([], [], "ko", markersize=3)

        def init() -> tuple[Line2D, ...]:
            line.set_data([], [])
            head.set_data([], [])
            tail.set_data([], [])
            return line, head, tail

        def update(i: int) -> tuple[Line2D, ...]:
            xf, yf = frames[i]
            line.set_data(xf, yf)
            head.set_data([xf[0]], [yf[0]])
            tail.set_data([xf[-1]], [yf[-1]])
            return line, head, tail

        ani = FuncAnimation(fig, update, frames=len(frames), init_func=init, blit=True)
        if output_path.endswith(".mp4"):
            ani.save(output_path, writer="ffmpeg", fps=50)
        plt.close()
        return ani
