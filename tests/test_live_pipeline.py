import os
import tempfile
import unittest

from src.connectoview import (
    MESH_OPACITY_DEFAULT,
    INPUT_COLOR,
    OUTPUT_COLOR,
    build_neuprint_figure,
    export_neuprint_html,
    parse_obj_mesh,
    skeleton_to_line_xyz,
    synthetic_mesh,
    synthetic_skeleton,
    synthetic_synapses,
)


class LivePipelineOfflineTests(unittest.TestCase):
    def test_palette_and_opacity_constants(self):
        self.assertEqual(INPUT_COLOR, "#3B82F6")
        self.assertEqual(OUTPUT_COLOR, "#EF4444")
        self.assertEqual(MESH_OPACITY_DEFAULT, 0.15)

    def test_skeleton_segments_skip_root(self):
        skel = synthetic_skeleton(123, n=10, seed=0)
        xs, _, _ = skeleton_to_line_xyz(skel)
        # 9 parented nodes -> 9 segments x 3 entries (child, parent, None)
        self.assertEqual(len(xs), 9 * 3)

    def test_corrupt_synapses_omitted(self):
        pre, post = synthetic_synapses(123, seed=0)
        self.assertFalse(pre.isna().any().any())
        self.assertFalse(post.isna().any().any())
        self.assertEqual(len(pre), 120)
        self.assertEqual(len(post), 180)

    def test_obj_parse_and_bad_input(self):
        raw = b"v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n"
        x, y, z, i, j, k = parse_obj_mesh(raw)
        self.assertEqual(len(x), 3)
        self.assertEqual((i[0], j[0], k[0]), (0, 1, 2))
        with self.assertRaises(ValueError):
            parse_obj_mesh(b"v 0 0 0\n")

    def test_figure_traces_and_export(self):
        skeletons = {1: synthetic_skeleton(1, seed=0), 2: synthetic_skeleton(2, seed=7)}
        synapses = {1: synthetic_synapses(1, seed=0), 2: synthetic_synapses(2, seed=13)}
        meshes = {"MB(R)": synthetic_mesh()}
        fig = build_neuprint_figure(skeletons, synapses, meshes)
        names = [t.name for t in fig.data]
        self.assertTrue(any(n.startswith("Neuron") for n in names))
        self.assertTrue(any("Inputs" in n for n in names))
        self.assertTrue(any("Outputs" in n for n in names))
        self.assertTrue(any(n.startswith("ROI") for n in names))
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "t.html")
            size = export_neuprint_html(fig, out)
            self.assertLess(size, 5 * 1024 * 1024)
            with open(out, encoding="utf-8", errors="ignore") as fh:
                html = fh.read()
            self.assertIn("<html", html.lower())
            self.assertIn("39FF14", html)  # neon green neuron
            self.assertIn("0.15", html)  # mesh opacity default


if __name__ == "__main__":
    unittest.main()
