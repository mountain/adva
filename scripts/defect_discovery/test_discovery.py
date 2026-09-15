"""Controls for false-green reports, mutations, and unintended/duplicate publication."""
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import probes
import run
import upstream
import verify


class DiscoveryTests(unittest.TestCase):
    def test_exp_checker_rejects_inward_lower_bound(self):
        self.assertTrue(probes.exp_boundary_ok("1/3", "3"))
        self.assertFalse(probes.exp_boundary_ok("1", "3"))
        self.assertFalse(probes.exp_boundary_ok("1/3", "2"))

    def test_inverse_checker_rejects_missing_normalization(self):
        self.assertTrue(probes.inverse_ok("2", {"0,0": "1/2"}))
        self.assertFalse(probes.inverse_ok("2", {"0,0": "1"}))
        self.assertFalse(probes.inverse_ok("2", {"0,0": "1/2", "1,0": "1"}))

    def test_errors_and_disagreement_never_pass(self):
        self.assertEqual(run.classify([]), "Unknown")
        self.assertEqual(run.classify([{"unknown_reason": "timeout"}] * 2), "Unknown")
        a = {"result": {"cases": [{"verdict": "Pass"}]}, "result_sha256": "a"}
        self.assertEqual(run.classify([a, {**a, "result_sha256": "b"}]), "Unknown")
        self.assertEqual(run.classify([a, a]), "BoundedPass")
        b = {"result": {"cases": [{"verdict": "Violation"}]}, "result_sha256": "b"}
        self.assertEqual(run.classify([b, b]), "NativeReproduced")
        c = {"result": {"cases": [{"verdict": "unexpected"}]}, "result_sha256": "c"}
        self.assertEqual(run.classify([c, c]), "Unknown")
        d = {"result": {"cases": []}, "result_sha256": "d"}
        self.assertEqual(run.classify([d, d]), "Unknown")

    def test_resource_installation_failure_blocks_target(self):
        with patch("run.platform.system", return_value="Linux"), patch("resource.setrlimit", side_effect=OSError("denied")), patch("run.run") as target:
            with self.assertRaises(OSError):
                run.worker("exp-cross-zero", pathlib.Path("."))
            target.assert_not_called()

    def test_incomplete_report_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(OSError):
            verify.verify(pathlib.Path(tmp))

    def test_changed_report_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "COMPLETE.json").write_bytes(run.encode({"sha256": {"report.json": "old", "report.md": "old"}}))
            (root / "report.json").write_text("changed")
            with self.assertRaises(ValueError):
                verify.verify(root)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.candidate = self.root / "candidate.json"
        self.package = self.root / "package"
        self.data = {k: "reviewed test fixture" for k in (
            "title", "upstream_version", "invariant", "witness_key", "impact",
            "open_obligations", "policy_review", "dedup_review", "reviewed_by", "checked_at")}
        self.data.update(target="example/project", contract_url="https://example.org/contract",
                         classification="UpstreamContractViolation", disclosure="PublicNonSecurity",
                         public_payload_reviewed=True, target_allows_submission=True)
        source = b"# TEST FIXTURE ONLY: not an actual upstream reproduction\n"
        (self.root / "reproducer.py").write_bytes(source)
        record = dict(evidence="ActualUpstreamReproduction", violation=True,
                      reproducer_sha256=upstream.sha(source), command="test fixture",
                      environment="mock", expected="expected", actual="observed")
        for n in (1, 2):
            (self.root / f"run-{n}.json").write_bytes(upstream.dump({**record, "execution_id": f"fixture-{n}", "executed_at": "2026-09-15"}))

    def prepare(self):
        self.candidate.write_bytes(upstream.dump(self.data))
        upstream.prepare(self.candidate, self.package)

    def test_local_finding_cannot_be_prepared(self):
        self.data["classification"] = "NativeReproduced"
        with self.assertRaises(ValueError):
            self.prepare()

    def test_sensitive_finding_not_public(self):
        self.data["disclosure"] = "SecuritySensitive"
        with self.assertRaises(ValueError):
            self.prepare()

    def test_duplicate_replay_identity_rejected(self):
        (self.root / "run-2.json").write_bytes((self.root / "run-1.json").read_bytes())
        with self.assertRaises(ValueError):
            self.prepare()

    def test_artifact_tampering_blocks_even_dry_run(self):
        self.prepare()
        (self.package / "issue.md").write_text("changed")
        with patch("upstream.gh") as network, self.assertRaises(ValueError):
            upstream.submit(self.package, False)
        network.assert_not_called()

    def test_default_has_no_network_effect(self):
        self.prepare()
        with patch("upstream.gh") as network:
            self.assertEqual(upstream.submit(self.package, False)["state"], "DryRun")
        network.assert_not_called()

    def test_existing_issue_not_duplicated(self):
        self.prepare()
        payload = upstream.verify(self.package)
        issue = dict(html_url="https://github.com/example/project/issues/42", body=payload["body"])
        with patch("upstream.gh", side_effect=[{}, {"items": [issue], "total_count": 1}, issue]) as network:
            receipt = upstream.submit(self.package, True)
        self.assertEqual(receipt["state"], "ExistingIssueNoNewContent")
        self.assertTrue(all("POST" not in c.args for c in network.call_args_list))

    def test_ambiguous_create_is_not_retried(self):
        self.prepare()
        with patch("upstream.gh", side_effect=[{}, {"items": [], "total_count": 0}, RuntimeError("network lost")]):
            with self.assertRaises(RuntimeError):
                upstream.submit(self.package, True)
        with patch("upstream.gh") as network, self.assertRaises(RuntimeError):
            upstream.submit(self.package, True)
        network.assert_not_called()

    def test_success_retains_receipt_and_second_call_is_local(self):
        self.prepare()
        payload = upstream.verify(self.package)
        issue = dict(html_url="https://github.com/example/project/issues/42", body=payload["body"])
        with patch("upstream.gh", side_effect=[{}, {"items": [], "total_count": 0}, issue]):
            receipt = upstream.submit(self.package, True)
        self.assertEqual(receipt["state"], "SubmittedNotUpstreamConfirmed")
        with patch("upstream.gh") as network:
            self.assertEqual(upstream.submit(self.package, True), receipt)
        network.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
