import unittest

from src.connectoview import build_html, demo_scene


class ConnectoViewTests(unittest.TestCase):
    def test_demo_html_is_self_describing(self):
        html = build_html(demo_scene())
        self.assertIn("Synthetic demonstration data", html)
        self.assertIn("plotly-2.35.2", html)
        self.assertIn("Input synapses", html)
        self.assertIn("Output synapses", html)
        self.assertIn("Demo ROI envelope", html)

    def test_demo_has_two_neurons_and_two_synapse_classes(self):
        scene = demo_scene()
        self.assertEqual(2, len(scene.neurons))
        self.assertGreater(len(scene.inputs), 0)
        self.assertGreater(len(scene.outputs), 0)


if __name__ == "__main__":
    unittest.main()
