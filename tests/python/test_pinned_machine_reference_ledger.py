"""Original synthetic files only. No production capture, fixture or receiver."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import inventory_pinned_machine_reference_ledger as driver


class ReferenceLedgerTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.machine = root / "machine"
        self.run = root / "attempt"
        self.digest = "f" * 64
        self.machine.mkdir()
        self.files = {"Cargo.toml": b"REQUEST receive OutsideTextSentinel\r\n" * 120,
                      "pyproject.toml": b"ordinary line\n",
                      "spec/catalog.json": b'{"files":{}}\n',
                      "toolchain/cli.py": b"unmatched\nOUTCOME\n",
                      "exchange_routine/cli.py": b""}
        for path, data in self.files.items():
            dest = self.machine / path
            dest.parent.mkdir(exist_ok=True)
            dest.write_bytes(data)
        git = ["git", "-C", str(self.machine)]
        subprocess.run(git + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "."], check=True)
        subprocess.run(git + ["-c", "user.name=Synthetic", "-c", "user.email=fixture@example.invalid",
                              "commit", "-qm", "synthetic surface"], check=True)
        pin = subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()
        self.enterContext(patch.object(driver.prior, "EXPECTED_REVISION", pin))
        manifest = [{"path": p, "bytes": len(b), "sha256": driver.sha(b)}
                    for p, b in sorted(self.files.items())]
        self.anchor = {"files": len(manifest), "bytes": sum(map(len, self.files.values())),
                       "sha256": driver.sha(driver.encode(manifest)), "candidate_lines": 121}

    def capture(self):
        return driver.capture(self.machine, self.run, self.anchor, self.digest)

    def verify(self):
        return driver.verify(self.run, self.anchor, self.digest)

    def failed(self, reason, phase):
        self.assertNotEqual(self.capture(), 0)
        failure = driver.load_json(self.run / "failure.json")
        self.assertEqual((failure["status"], failure["reason"], failure["phase"]),
                         ("Unknown", reason, phase))
        self.assertFalse((self.run / "receipt.json").exists())
        with self.assertRaises((OSError, ValueError)):
            self.verify()

    def test_closed_stdout_retains_every_reference(self):
        read, write = os.pipe()
        os.close(read)
        original = os.dup(1)
        try:
            os.dup2(write, 1)
            self.assertEqual(self.capture(), 0)
        finally:
            os.dup2(original, 1)
            os.close(original)
            os.close(write)
        self.assertTrue(self.verify())
        data = (self.run / "references.jsonl").read_bytes()
        self.assertGreater(len(data), 4096)
        self.assertNotIn(b"OutsideTextSentinel", data)
        rows = [json.loads(row) for row in data.splitlines()]
        self.assertEqual(rows, [{"path": "Cargo.toml", "line": n, "terms": ["receive", "request"]}
                                for n in range(1, 121)] +
                         [{"path": "toolchain/cli.py", "line": 2, "terms": ["outcome"]}])

    def test_truncated_ledger_after_commit(self):
        self.assertEqual(self.capture(), 0)
        path = self.run / "references.jsonl"
        path.write_bytes(path.read_bytes()[:-2])
        with self.assertRaises(ValueError):
            self.verify()

    def test_silent_loss_before_readback(self):
        original = driver.check_evidence
        def drop(run, anchor, ledger):
            path = run / "references.jsonl"
            path.write_bytes(path.read_bytes().split(b'\n', 1)[1])
            return original(run, anchor, ledger)
        with patch.object(driver, "check_evidence", drop):
            self.failed("EvidenceCaptureFailure", "readback")

    def test_hard_kill_after_partial_write(self):
        def die(f, rows):
            row = next(iter(rows))
            f.write(driver.encode(row) + b'\n')
            f.flush()
            os.kill(os.getpid(), signal.SIGKILL)
        with patch.object(driver, "write_references", die):
            self.assertNotEqual(self.capture(), 0)
        self.assertFalse((self.run / "references.jsonl").exists())
        self.assertTrue((self.run / "manifest.json").is_file())
        self.assertEqual(driver.load_json(self.run / "supervisor.json")["worker_exit"], -signal.SIGKILL)
        self.assertEqual(driver.load_json(self.run / "phase.json")["phase"], "content_search_and_write")
        with self.assertRaises((OSError, ValueError)):
            self.verify()
        with self.assertRaises(FileExistsError):
            self.capture()

    def test_write_error_after_first_record(self):
        def fail(f, rows):
            f.write(driver.encode(next(iter(rows))))
            raise OSError(28, "synthetic no space")
        with patch.object(driver, "write_references", fail):
            self.failed("EvidenceCaptureFailure", "content_search_and_write")
        self.assertFalse((self.run / "references.jsonl").exists())

    def test_missing_file_before_search(self):
        (self.machine / "Cargo.toml").unlink()
        self.failed("RefusedBeforeSearch", "preflight")
        self.assertFalse((self.run / "manifest.json").exists())

    def test_dirty_same_length_after_manifest(self):
        original = driver.references
        def changed(machine, manifest):
            (machine / "pyproject.toml").write_bytes(b"x" * len(self.files["pyproject.toml"]))
            return original(machine, manifest)
        with patch.object(driver, "references", changed):
            self.failed("RefusedDuringSearch", "content_search_and_write")

    def test_missing_during_search_after_positive_rows(self):
        original = driver.references
        def missing(machine, manifest):
            (machine / "pyproject.toml").unlink()
            return original(machine, manifest)
        with patch.object(driver, "references", missing):
            self.failed("RefusedDuringSearch", "content_search_and_write")
        failure = driver.load_json(self.run / "failure.json")
        self.assertEqual((failure["path"], failure["exception"]), ("pyproject.toml", "FileNotFoundError"))
        self.assertTrue((self.run / "manifest.json").exists())

    def test_decode_error_after_valid_manifest(self):
        path = self.machine / "pyproject.toml"
        path.write_bytes(b"\xff")
        manifest = [{"path": "pyproject.toml", "bytes": 1, "sha256": driver.sha(b"\xff")}]
        self.anchor.update(files=1, bytes=1, sha256=driver.sha(driver.encode(manifest)))
        with patch.object(driver.prior, "preflight", return_value=(manifest, self.anchor["sha256"])):
            self.failed("RefusedDuringSearch", "content_search_and_write")
        self.assertEqual(driver.load_json(self.run / "failure.json")["exception"], "UnicodeDecodeError")

    def test_wall_deadline_inside_blocked_read(self):
        original = driver.regular_bytes
        def slow(path, limit):
            if path == self.machine / "Cargo.toml":
                time.sleep(2)
            return original(path, limit)
        with patch.object(driver, "regular_bytes", slow), patch.object(driver.prior, "MAX_SEARCH_NS", 70_000_000):
            self.failed("RefusedDuringSearch", "content_search_and_write")

    def test_refuse_reentrant_and_repeated_attempts(self):
        self.assertEqual(self.capture(), 0)
        h = self.verify()
        with self.assertRaises(FileExistsError):
            self.capture()
        self.assertEqual(self.verify(), h)

    def test_final_receipt_directory_sync_error(self):
        original = driver.sync_dir
        def fail(path):
            if (self.run / "receipt.json").exists():
                raise OSError("synthetic fsync failure")
            original(path)
        with patch.object(driver, "sync_dir", fail):
            self.failed("EvidenceCaptureFailure", "receipt_commit")

    def test_manifest_corruption_after_commit(self):
        self.assertEqual(self.capture(), 0)
        path = self.run / "manifest.json"
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaises(ValueError):
            self.verify()

    def test_wrong_anchor_candidate_count(self):
        self.anchor["candidate_lines"] -= 1
        self.failed("EvidenceCaptureFailure", "content_search_and_write")

    def test_missing_supervisor_never_verifies(self):
        self.assertEqual(self.capture(), 0)
        (self.run / "supervisor.json").unlink()
        with self.assertRaises(OSError):
            self.verify()


if __name__ == "__main__":
    unittest.main()
