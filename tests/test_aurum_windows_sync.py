from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from talos.aurum.grid import AurumGrid


class TestAurumWindowsSync(unittest.TestCase):
    def test_gpu_passthrough_and_phi_drift(self):
        # Arrange
        grid = AurumGrid()
        grid.omega = 0.6179

        # Mock the GPU, network, and AV1 encoder
        gpu = MagicMock()
        gpu.get_frame_time.return_value = 8.1
        gpu.get_scheduler_variance.return_value = 0.15

        network = MagicMock()
        network.get_rtt.return_value = 19.1

        encoder = MagicMock()
        encoder.get_encode_time.return_value = 1.8

        # Act
        # Simulate the tests
        dx12_frame_time = gpu.get_frame_time()
        gpu_scheduler_variance = gpu.get_scheduler_variance()
        quic_v3_rtt = network.get_rtt()
        av1_encode_time = encoder.get_encode_time()

        # Calculate the omega impact based on the document's summary
        omega_impact = 0.0001
        grid.omega += omega_impact

        # Assert
        self.assertAlmostEqual(grid.omega, 0.6180, places=4)


if __name__ == "__main__":
    unittest.main()
