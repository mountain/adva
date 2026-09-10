"""Pre-launch budget containment; runnable without the native extension."""

import importlib.util
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "adva_quine_cpu_budget_test", ROOT / "python/adva/quine_relay.py"
)
relay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(relay)


class QuineCpuBudgetTests(unittest.TestCase):
    def supervisor(self, output, remaining, per_child=5):
        limits = {
            "wall_seconds": 60,
            "aggregate_child_cpu_seconds": remaining,
            "child_cpu_seconds": per_child,
            "address_space_bytes": 2**31,
            "max_file_bytes": 2**20,
            "max_processes": 3,
        }
        return relay.Supervisor(output, limits)

    def test_refuses_before_launch_or_artifacts(self):
        for remaining in (0.0, 0.25, math.nextafter(1.0, 0.0)):
            with self.subTest(remaining=remaining), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp)
                with patch.object(relay.Supervisor, "child_cpu", return_value=0.0):
                    supervisor = self.supervisor(output, remaining)
                    with (
                        patch.object(relay.subprocess, "Popen") as launch,
                        self.assertRaises(relay.Exhausted),
                    ):
                        supervisor.call("refused", ["never-run"], output)
                    launch.assert_not_called()
                    self.assertEqual(supervisor.calls, [])
                    self.assertEqual(list(output.iterdir()), [])

    def test_installed_limit_stays_inside_both_budgets(self):
        cases = ((1.0, 5, 1), (1.25, 5, 1), (2.0, 5, 2), (8.75, 3, 3))
        for remaining, per_child, expected in cases:
            with (
                self.subTest(remaining=remaining),
                patch.object(relay.Supervisor, "child_cpu", return_value=0.0),
            ):
                supervisor = self.supervisor(Path("unused"), remaining, per_child)
                cpu = supervisor.child_cpu_limit()
                with patch.object(relay.resource, "setrlimit") as install:
                    supervisor.restrictions(cpu)
                install.assert_any_call(relay.resource.RLIMIT_CPU, (expected, expected))
                self.assertLessEqual(expected, remaining)
                self.assertLessEqual(expected, per_child)

    def test_parent_allowance_is_installed_without_reading_child_accounting(self):
        with (
            patch.object(relay.Supervisor, "child_cpu", return_value=0.0),
            tempfile.TemporaryDirectory() as tmp,
        ):
            output = Path(tmp)
            supervisor = self.supervisor(output, 10)

            def fork(*args, **kwargs):
                # A fresh child's RUSAGE_CHILDREN would be zero. It must
                # never be consulted to revise the parent's allowance.
                with patch.object(relay.Supervisor, "child_cpu", side_effect=AssertionError):
                    kwargs["preexec_fn"]()
                return Mock(pid=123, returncode=0)

            with (
                patch.object(relay.Supervisor, "child_cpu", return_value=6.25),
                patch.object(relay.subprocess, "Popen", side_effect=fork),
                patch.object(relay.resource, "setrlimit") as install,
                patch.object(relay.os, "killpg"),
            ):
                supervisor.call("parent-budget", ["mock-child"], output)
            install.assert_any_call(relay.resource.RLIMIT_CPU, (3, 3))
            self.assertEqual(len(supervisor.calls), 1)

    def test_fractional_per_child_cap_is_not_rounded_up(self):
        with patch.object(relay.Supervisor, "child_cpu", return_value=0.0):
            supervisor = self.supervisor(Path("unused"), 10, per_child=0.5)
            with self.assertRaises(relay.Exhausted):
                supervisor.child_cpu_limit()

    def test_post_execution_exhaustion_check_is_retained(self):
        with patch.object(relay.Supervisor, "child_cpu", return_value=0.0):
            supervisor = self.supervisor(Path("unused"), 2)
        with (
            patch.object(relay.Supervisor, "child_cpu", return_value=2.01),
            self.assertRaisesRegex(relay.Exhausted, "aggregate child CPU"),
        ):
            supervisor.check()

    def test_admitted_real_child_can_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            supervisor = self.supervisor(output, 3, per_child=2)
            supervisor.call("admitted", [relay.sys.executable, "-c", "print('ok')"], output)
            self.assertEqual((output / "admitted.stdout").read_text().strip(), "ok")
            self.assertEqual(supervisor.calls[0]["exit_code"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
