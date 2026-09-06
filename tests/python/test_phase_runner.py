"""Synthetic subprocess protocol tests; fixtures are NOT native adva evidence."""

import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest


SOURCE = Path(__file__).resolve().parents[2] / "experiments/phase_runner/run_six.py"
SPEC = importlib.util.spec_from_file_location("phase_runner", SOURCE)
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)

CHILD = '''# Synthetic fixture, not adva.
import json, pathlib, subprocess, sys, time
mode, s, m, r, t, f = sys.argv[1:]
subject = json.loads(pathlib.Path(s).read_text())
if mode == "descendant":
    marker = t + ".descendant-output"
    source = "import pathlib,sys,time; time.sleep(0.2); pathlib.Path(sys.argv[1]).write_text('survived')"
    descendant = subprocess.Popen([sys.executable, "-c", source, marker])
    pathlib.Path(t + ".child-pid").write_text(str(descendant.pid))
if mode == "timeout":
    time.sleep(5)
next_state = dict(subject)
next_state["count"] = subject["count"] + 1
next_state["history"] = subject.get("history", []) + [{"guard": {"state": "failed" if mode == "guard" else "passed"}}]
transition = {"schema": "synthetic.transition.v0", "version": 0, "input": subject, "output": next_state}
if mode == "bad_frontier_version":
    next_state["version"] = 1
if mode == "bool_frontier_version":
    next_state["version"] = False
if mode == "bad_transition_version":
    transition["version"] = "0"
pathlib.Path(t).write_text(json.dumps(transition))
if mode == "partial":
    print("synthetic partial save", file=sys.stderr)
    sys.exit(7)
pathlib.Path(f).write_text(json.dumps(next_state))
'''


class PhaseRunnerTest(unittest.TestCase):
    def setup_contract(self, base, mode="normal", free_adapter=False):
        (base / "child.py").write_text(CHILD)
        (base / "subject.json").write_text(json.dumps({"schema": "synthetic.frontier.v0", "version": 0, "count": 0}))
        for name in ("method", "resource"):
            (base / f"{name}.json").write_text("{}")
        template = ["{backend}", str(base / "child.py"), mode, "{subject}", "{method}", "{resource}", "{transition}", "{frontier}"]
        phases = [{"name": name, "requested_slots": 6, "initial_subject": "subject.json",
                   "method": "method.json", "resource": "resource.json",
                   "command_template": template if name == "learn" or free_adapter else None,
                   "expected_transition_schema": "synthetic.transition.v0",
                   "expected_frontier_schema": "synthetic.frontier.v0"} for name in ("learn", "free")]
        if not free_adapter:
            for key in ("initial_subject", "method", "resource", "expected_transition_schema", "expected_frontier_schema"):
                phases[1][key] = None
        contract = {"schema": RUNNER.SCHEMA, "version": 0, "phases": phases,
                    "limits": dict(RUNNER.CAPS, call_timeout_seconds=0.15 if mode == "timeout" else 3)}
        path = base / "contract.json"
        path.write_text(json.dumps(contract))
        return path

    def invoke(self, base, contract, backend=True):
        command = ["--contract", str(contract), "--report-dir", str(base / "reports")]
        if backend:
            command += ["--backend", sys.executable]
        code = RUNNER.main(command)
        report = json.loads((base / "reports/run-report.json").read_text())
        return code, report

    def test_synthetic_six_state_chaining_and_missing_free_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            code, result = self.invoke(base, self.setup_contract(base))
            self.assertEqual(code, 0)
            learn, free = result["phases"]
            self.assertEqual(learn["actual_launches"], 6)
            self.assertEqual(learn["status"], "Completed")
            self.assertEqual(json.loads(Path(learn["final_frontier"]).read_text())["count"], 6)
            self.assertEqual(free["reason"], "AdapterUnavailable")
            self.assertEqual(free["actual_launches"], 0)
            self.assertEqual(len(free["steps"]), 6)

    def test_synthetic_nonzero_exit_retains_partial_save(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            code, result = self.invoke(base, self.setup_contract(base, "partial"))
            learn, free = result["phases"]
            self.assertEqual(code, 1)
            self.assertEqual(learn["actual_launches"], 1)
            self.assertEqual(learn["steps"][0]["return_code"], 7)
            self.assertTrue(learn["steps"][0]["partial_save"])
            self.assertEqual(len(learn["steps"][0]["output_bindings"]), 1)
            self.assertEqual(free["actual_launches"], 0)

    def test_synthetic_timeout_stops_without_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            _, result = self.invoke(base, self.setup_contract(base, "timeout"))
            learn = result["phases"][0]
            self.assertEqual(learn["reason"], "CallTimedOut")
            self.assertEqual(learn["actual_launches"], 1)
            self.assertEqual(learn["steps"][1]["status"], "NotRun")

    def test_backend_unavailable_launches_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            code, result = self.invoke(base, self.setup_contract(base), backend=False)
            self.assertEqual(code, 0)
            self.assertEqual(result["actual_launches"], 0)
            self.assertEqual(result["phases"][0]["reason"], "BackendUnavailable")
            self.assertFalse(result["native_semantics_implemented_here"])

    def test_synthetic_guard_failure_stops_even_with_zero_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            _, result = self.invoke(base, self.setup_contract(base, "guard"))
            learn = result["phases"][0]
            self.assertEqual(learn["status"], "Rejected")
            self.assertEqual(learn["actual_launches"], 1)
            self.assertEqual(learn["steps"][1]["status"], "NotRun")

    def test_backend_binding_is_complete_or_explicitly_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic-binary"
            path.write_bytes(b"synthetic fixture bytes")
            binding = RUNNER.backend_binding(path)
            self.assertEqual(binding["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(binding["bytes"], path.stat().st_size)
            oversized = RUNNER.backend_binding(path, cap=3)
            self.assertIsNone(oversized["sha256"])
            self.assertIsNone(oversized["bytes"])
            self.assertEqual(oversized["reason"], "BackendExceedsHashLimit")
            self.assertEqual(RUNNER.backend_binding(None)["reason"], "BackendUnavailable")

    def test_output_versions_require_integer_zero(self):
        for mode in ("bad_frontier_version", "bool_frontier_version", "bad_transition_version"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                code, result = self.invoke(base, self.setup_contract(base, mode))
                self.assertEqual(code, 1)
                self.assertEqual(result["actual_launches"], 1)
                self.assertIn("exact integer zero", result["phases"][0]["reason"])
                self.assertEqual(result["backend_binding"]["reason"], "CompleteFileHash")

    def test_completed_leader_cannot_leave_same_group_descendant(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            code, result = self.invoke(base, self.setup_contract(base, "descendant"))
            learn = result["phases"][0]
            self.assertEqual(code, 0)
            self.assertEqual(learn["status"], "Completed")
            pid_files = list((base / "reports").glob("*.child-pid"))
            self.assertEqual(len(pid_files), 6)
            time.sleep(0.3)  # Longer than the fixture's delayed write, not a research wait.
            self.assertFalse(list((base / "reports").glob("*.descendant-output")))
            for path in pid_files:
                stat = Path("/proc") / path.read_text() / "stat"
                if stat.exists():
                    self.assertEqual(stat.read_text().split(") ", 1)[1].split()[0], "Z")
            self.assertTrue(all(row["process_group_cleanup"] in ("SignalSent", "AlreadyExited")
                                for row in learn["steps"]))


if __name__ == "__main__":
    unittest.main()
