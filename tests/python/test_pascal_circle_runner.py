"""Budget and coupled-fit regressions without repeating the search campaign."""
from fractions import Fraction as F
import json
from pathlib import Path
import tempfile
import unittest

from experiments.pascal_circle_learning import model
from experiments.pascal_circle_learning import run as runner


class PascalCircleRunnerTests(unittest.TestCase):
    def test_zero_and_insufficient_fuel_do_not_run_proposer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed = root / "original-synthetic-seed.json"
            seed.write_text(json.dumps({"schema": "adva.external.pascal-circle-seed.v0",
                                       "points": [[i, i * i] for i in range(14)]}))
            for fuel in (0, runner.NUMERICAL_EVALUATIONS):
                report = runner.run(seed, root / ("run-" + str(fuel)), fuel)
                self.assertEqual(report["status"], "Unknown")
                self.assertEqual(report["reason"], "insufficient-fuel-for-fixed-proposal-and-one-check")
                self.assertEqual(report["children"], [])
                self.assertEqual(report["fuel_spent"], 0)
                self.assertEqual(report["fuel_remaining"], fuel)
                self.assertEqual(report["rationalization_attempts"], [])

    def test_missing_seed_is_explicit_and_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "run"
            report = runner.run(root / "absent.json", output)
            self.assertEqual(report["status"], "Unknown")
            self.assertEqual(report["reason"], "required-input-unavailable")
            self.assertEqual(report["children"], [])
            retained = (output / "report.json").read_bytes()
            with self.assertRaises(FileExistsError):
                runner.run(root / "absent.json", output)
            self.assertEqual((output / "report.json").read_bytes(), retained)

    def test_joint_fit_recovers_coupled_center_construction(self):
        red, blue = model.unit_groups([F(0), F(1, 3), F(2), F(-1, 2)],
                                      [F(0), F(1, 2), F(3), F(-2)])
        k = model.circle_point(F(1, 2))
        center, q, s = 2 + 3j, 4 - 2j, 1 + 2j
        target = [None] * 14
        for index, point in zip(model.RED_GROUP, red, strict=True):
            value = center + q * complex(*map(float, point))
            target[index] = [value.real, value.imag]
        for index, point in zip(model.BLUE_GROUP, blue, strict=True):
            value = center + q * complex(*map(float, k)) + s * complex(*map(float, point))
            target[index] = [value.real, value.imag]
        fitted = runner.fit_joint(red, blue, k, target)
        for actual, expected in zip(fitted, (center, q, s), strict=True):
            self.assertLess(abs(actual - expected), 1e-10)


if __name__ == "__main__":
    unittest.main()
