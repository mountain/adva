"""Finite geometric negative controls; these do not assert infinite tiling."""

from fractions import Fraction as F
import importlib.util
from math import comb
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "pascal_spectre_patch", ROOT / "experiments/pascal_spectre_patch/patch.py")
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)


class CurvedPatchControls(unittest.TestCase):
    def test_bernstein_coefficients_and_seam_identity(self):
        a, b, eps = (F(2, 3), F(-5, 7)), (F(-4, 9), F(11, 13)), F(1, 1000)
        controls = patch.controls(a, b, eps)
        for t in (F(0), F(1, 11), F(1, 4), F(1, 2), F(7, 9), F(1)):
            bernstein = tuple(sum(F(comb(5, i)) * t ** i * (1-t) ** (5-i) * controls[i][k]
                                  for i in range(6)) for k in (0, 1))
            self.assertEqual(bernstein, patch.curve(a, b, eps, t))
            self.assertEqual(patch.curve(a, b, eps, t), patch.curve(b, a, eps, 1-t))
            reflected = tuple(a[k] + b[k] - patch.curve(a, b, eps, t)[k] for k in (0, 1))
            self.assertEqual(reflected, patch.curve(a, b, eps, 1-t))

    def test_crossing_hulls_fail_but_shared_endpoint_is_allowed(self):
        def edge(a, b):
            return {"a": tuple(map(F, a)), "b": tuple(map(F, b)), "incidences": []}
        crossed = [edge((-1, 0), (1, 0)), edge((0, -1), (0, 1))]
        self.assertEqual(patch.certify_hulls(crossed, F(1, 100), patch.Budget())["status"],
                         "RefutedSufficientCondition")
        adjacent = [edge((0, 0), (1, 0)), edge((1, 0), (1, 1))]
        self.assertEqual(patch.certify_hulls(adjacent, F(1, 100), patch.Budget())["status"],
                         "Verified")

    def test_overlap_checker_distinguishes_seam_from_interior(self):
        square = [(F(0), F(0)), (F(1), F(0)), (F(1), F(1)), (F(0), F(1))]
        triangles = patch.triangulate(square)
        neighbor = [(x + 1, y) for x, y in square]
        overlapping = [(x + F(1, 2), y) for x, y in square]
        self.assertIsNone(patch.interior_overlap(square, neighbor, triangles, patch.Budget()))
        self.assertIsNotNone(patch.interior_overlap(square, overlapping, triangles, patch.Budget()))

    def test_inverse_stereographic_is_exact_but_changes_lengths(self):
        a, b, c = (F(0), F(0)), (F(1), F(0)), (F(2), F(0))
        xyz = [patch.sphere_check(p, patch.Budget()) for p in (a, b, c)]
        chords = [sum((xyz[i][k] - xyz[i+1][k]) ** 2 for k in range(3)) for i in (0, 1)]
        self.assertEqual(chords, [F(2), F(2, 5)])

    def test_geometry_fuel_does_not_reset(self):
        budget = patch.Budget()
        budget.checks = patch.LIMITS["exact_geometry_checks"]
        with self.assertRaises(TimeoutError):
            budget.check()
        with self.assertRaises(TimeoutError):
            budget.check()


if __name__ == "__main__":
    unittest.main()
