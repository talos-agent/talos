import unittest
import numpy as np

from src.controllers.z_adaptive_controller import ZAdaptiveController, ZNConfig

class TestZAdaptiveController(unittest.TestCase):

    def test_controller_instantiation(self):
        """Test that the controller can be instantiated with a config."""
        cfg = ZNConfig()
        controller = ZAdaptiveController(cfg)
        self.assertIsInstance(controller, ZAdaptiveController)
        self.assertEqual(controller.a_hat, 0.0)
        self.assertEqual(controller.b_hat, 1.0)

    def test_compute_control_logic(self):
        """Test the control logic under a simple condition."""
        cfg = ZNConfig(k_error=1.0)
        controller = ZAdaptiveController(cfg)

        # Test case where b_hat is stable
        u, e = controller._compute_control(x=1.0, x_ref=1.5, x_ref_next=1.5)
        self.assertAlmostEqual(e, -0.5)
        expected_u = (-0.0 * 1.0 - 1.0 * -0.5 + 0.0) / 1.0
        self.assertAlmostEqual(u, expected_u)

        # Test case where b_hat is near zero (fallback)
        controller.b_hat = 1e-7
        u, e = controller._compute_control(x=1.0, x_ref=1.5, x_ref_next=1.5)
        self.assertAlmostEqual(e, -0.5)
        expected_u_fallback = np.clip(-1.0 * -0.5, *cfg.u_sat)
        self.assertAlmostEqual(u, expected_u_fallback)

    def test_update_estimates_logic(self):
        """Test that the estimates are updated."""
        cfg = ZNConfig(gamma_a=0.1, gamma_b=0.1, reg=0.01, dt=0.1)
        controller = ZAdaptiveController(cfg)
        a_hat_before = controller.a_hat
        b_hat_before = controller.b_hat

        controller._update_estimates(x=1.0, u=0.5, e=-0.5)

        self.assertNotEqual(controller.a_hat, a_hat_before)
        self.assertNotEqual(controller.b_hat, b_hat_before)

        # Check calculation
        da = -0.1 * -0.5 * 1.0 - 0.01 * 0.0
        db = -0.1 * -0.5 * 0.5 - 0.01 * 1.0
        expected_a_hat = a_hat_before + 0.1 * da
        expected_b_hat = b_hat_before + 0.1 * db
        self.assertAlmostEqual(controller.a_hat, expected_a_hat)
        self.assertAlmostEqual(controller.b_hat, expected_b_hat)

if __name__ == '__main__':
    unittest.main()