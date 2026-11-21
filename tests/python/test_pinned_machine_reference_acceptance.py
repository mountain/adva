"""Post-capture verification on copies of receipts. No production scans."""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import verify_pinned_machine_reference_review as audit


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.run = Path(temp.name) / "capture"
        shutil.copytree(audit.capture.RUN, self.run)
        self.marker = self.run / "supervisor.json"

    def change_marker(self, **fields):
        value = audit.capture.load_json(self.marker)
        value.update(fields)
        audit.capture.save(self.marker, value)

    def test_original_complete_review(self):
        self.assertEqual(audit.verify_review(self.run)["rows_reviewed"], 430)

    def test_same_length_ledger_edit(self):
        path = self.run / "references.jsonl"
        raw = path.read_bytes()
        changed = raw.replace(b'"request"', b'"receive"', 1)
        self.assertNotEqual(raw, changed)
        self.assertEqual(len(raw), len(changed))
        path.write_bytes(changed)
        with self.assertRaisesRegex(ValueError, "ledger bytes or digest"):
            audit.verify_review(self.run)

    def test_contradictory_completion(self):
        self.change_marker(worker_status="Unknown")
        with self.assertRaisesRegex(ValueError, "finish cleanly"):
            audit.verify_review(self.run)

    def test_worker_budget_exceeded(self):
        self.change_marker(elapsed_ns=90_000_000_001)
        with self.assertRaisesRegex(ValueError, "supervisor time"):
            audit.verify_review(self.run)

    def test_supervisor_edit_within_budget(self):
        self.change_marker(elapsed_ns=4_000_000_000)
        with self.assertRaisesRegex(ValueError, "supervisor digest"):
            audit.verify_review(self.run)

    def test_search_budget_exceeded(self):
        receipt = audit.capture.load_json(self.run / "receipt.json")
        receipt.update(search_and_write_ns=30_000_000_001)
        with self.assertRaisesRegex(ValueError, "search time"):
            audit.check_completion(audit.capture.load_json(self.marker), receipt,
                                   audit.capture.load_json(audit.capture.CONTRACT))

    def test_stale_phase(self):
        audit.capture.save(self.run / "phase.json", {"contract_sha256": audit.CONTRACT_SHA256,
                                                     "phase": "readback"})
        with self.assertRaisesRegex(ValueError, "last phase"):
            audit.verify_review(self.run)

    def test_edited_classification_with_complete_coverage(self):
        path = self.run.parent / "review.json"
        raw = audit.REVIEW.read_bytes()
        changed = raw.replace(b'"decision": "NoExactRouteWithinSelectedSurface"',
                              b'"decision": "ExactRoute"')
        self.assertNotEqual(raw, changed)
        path.write_bytes(changed)
        with self.assertRaisesRegex(ValueError, "static review digest"):
            audit.verify_review(self.run, path)
