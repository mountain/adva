#!/usr/bin/env python3
"""Cross-check the frozen continuation gate with an independent Node receiver."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import tempfile
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NODE_RECEIVER = HERE / "receiver.mjs"
PYTHON_RECEIVER = ROOT / "experiments" / "continuation_resolution_gate" / "receiver.py"
PARENT = ROOT / "experiments" / "continuation_resolution_gate" / "evidence" / "attempt-2"
TERMINAL = ROOT / "experiments" / "terminal_resolution_receiver" / "evidence" / "attempt-1" / "cases"

CASES = (
    ("exact-alpha", "completed-alpha"),
    ("exact-gamma", "cancelled-gamma"),
    ("parent-unknown", "wrong-source"),
    ("parent-invalid", "noncanonical-terminal"),
    ("whole-object-substitution", "cancelled-gamma"),
    ("self-consistent-wrong-problem", "completed-alpha"),
    ("self-consistent-wrong-history", "completed-alpha"),
    ("changed-budget-under-old-query", "completed-alpha"),
    ("undeclared-replenishment-field", "completed-alpha"),
    ("noncanonical-continuation", "completed-alpha"),
)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha(path: Path) -> str:
    return digest(path.read_bytes())


def atomic_write_new(path: Path, value: object | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    raw = value if isinstance(value, bytes) else canonical(value)
    descriptor, temporary = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


class Campaign:
    def __init__(self, output: Path, child_timeout_seconds: float) -> None:
        self.output = output
        self.child_timeout_seconds = child_timeout_seconds
        self.started = time.monotonic()
        self.assertions = 0
        self.comparison_units = 0
        self.node_seconds = 0.0
        self.serialization_seconds = 0.0
        self.records: list[dict[str, object]] = []

    def check(self, condition: bool, label: str) -> None:
        self.assertions += 1
        if not condition:
            raise RuntimeError("CheckFailed:" + label)

    def save(self, path: Path, value: object | bytes) -> None:
        started = time.monotonic()
        atomic_write_new(path, value)
        self.serialization_seconds += time.monotonic() - started

    def compare(self, python: dict[str, object] | None, node: dict[str, object] | None,
                python_source: str, node_source: str) -> dict[str, object]:
        self.comparison_units += 1
        if python is None or node is None or python_source == node_source:
            return {"outcome": "UnknownImplementationAgreement", "reason": "MissingOrSameSource"}
        self.comparison_units += 2
        if python.get("outcome") != node.get("outcome"):
            return {"outcome": "UnknownImplementationAgreement", "reason": "ClassificationDivergence"}
        python_tuple = python.get("preserved_continuation")
        node_tuple = node.get("preserved_continuation")
        self.comparison_units += 1
        if canonical(python_tuple) != canonical(node_tuple):
            return {"outcome": "UnknownImplementationAgreement", "reason": "PreservedTupleDivergence"}
        return {"outcome": "ImplementationAgreement", "reason": "FiniteProjectionMatch"}

    def invoke(self, case_name: str, terminal_case: str,
               python_source: str, node_source: str) -> None:
        source = PARENT / "cases" / case_name
        query = source / "query.json"
        continuation = source / "continuation.json"
        resolution = TERMINAL / terminal_case / "receipt.json"
        python_receipt = json.loads((source / "receipt.json").read_bytes())
        before = {str(path.relative_to(ROOT)): file_sha(path)
                  for path in (query, continuation, resolution)}
        command = [
            "node", "--max-old-space-size=32", str(NODE_RECEIVER),
            "--query", str(query), "--continuation", str(continuation),
            "--resolution-receipt", str(resolution),
        ]
        started = time.monotonic()
        completed = subprocess.run(
            command,
            capture_output=True,
            timeout=self.child_timeout_seconds,
            check=False,
        )
        elapsed = time.monotonic() - started
        self.node_seconds += elapsed
        self.check(completed.returncode == 0, case_name + ":node-exit")
        self.check(len(completed.stdout) <= 16_384, case_name + ":stdout")
        self.check(len(completed.stderr) <= 4_096, case_name + ":stderr")
        node_receipt = json.loads(completed.stdout)
        after = {str(path.relative_to(ROOT)): file_sha(path)
                 for path in (query, continuation, resolution)}
        self.check(before == after, case_name + ":input-preservation")
        self.check(node_receipt["fuel_delta"] == 0, case_name + ":fuel")
        self.check(node_receipt["target_processes"] == 0, case_name + ":targets")
        self.check(all(node_receipt[key] is False for key in (
            "effect_authority", "retry_authority", "refund_authority",
            "mutation_authority", "native_authority", "free_authority"
        )), case_name + ":authority")
        comparison = self.compare(python_receipt, node_receipt, python_source, node_source)
        self.check(comparison["outcome"] == "ImplementationAgreement", case_name + ":agreement")
        work = node_receipt["work_units"]
        self.check(type(work) is int and 0 <= work <= 4_000, case_name + ":work")
        record = {
            "case": case_name,
            "terminal_case": terminal_case,
            "python_outcome": python_receipt["outcome"],
            "node_outcome": node_receipt["outcome"],
            "comparison": comparison,
            "node_work_units": work,
            "node_seconds": elapsed,
            "input_sha256_before": before,
            "input_sha256_after": after,
        }
        directory = self.output / "cases" / case_name
        self.save(directory / "node-receipt.json", node_receipt)
        self.save(directory / "comparison.json", comparison)
        self.records.append(record)


def main(output: Path, *, validation_timeout_seconds: float | None = None) -> int:
    if output.exists():
        raise SystemExit("output already exists")
    output.mkdir(parents=True)
    try:
        contract = json.loads((HERE / "contract.json").read_bytes())
        timeout_seconds = contract["limits"]["seconds_each"]
        execution_kind = "FrozenExecution"
        if validation_timeout_seconds is not None:
            validation = json.loads((HERE / "ci-validation-contract.json").read_bytes())
            if validation["status"] != "FrozenBeforeValidation":
                raise RuntimeError("InvalidValidationContractStatus")
            if file_sha(HERE / "contract.json") != validation["pins"]["contract_sha256"]:
                raise RuntimeError("ValidationContractPinMismatch")
            if file_sha(Path(__file__)) != validation["pins"]["runner_sha256"]:
                raise RuntimeError("ValidationRunnerPinMismatch")
            test_path = ROOT / "tests" / "python" / \
                "test_continuation_resolution_crosscheck.py"
            if file_sha(test_path) != validation["pins"]["test_sha256"]:
                raise RuntimeError("ValidationTestPinMismatch")
            if file_sha(NODE_RECEIVER) != validation["pins"]["node_receiver_sha256"]:
                raise RuntimeError("ValidationNodePinMismatch")
            timeout_seconds = validation_timeout_seconds
            if timeout_seconds != validation["limits"]["seconds_each"]:
                raise RuntimeError("UnfrozenValidationTimeout")
            execution_kind = "CiValidationReplay"
        campaign = Campaign(output, timeout_seconds)
        signal.signal(signal.SIGALRM,
                      lambda *_: (_ for _ in ()).throw(TimeoutError("CampaignWallLimit")))
        signal.setitimer(signal.ITIMER_REAL, contract["limits"]["outer_seconds"])
        campaign.check(contract["status"] == "FrozenBeforeExecution", "contract-status")
        campaign.check(file_sha(NODE_RECEIVER) == contract["pins"]["node_receiver_sha256"],
                       "node-source-pin")
        campaign.check(file_sha(PYTHON_RECEIVER) == contract["pins"]["python_receiver_sha256"],
                       "python-source-pin")
        campaign.check(file_sha(PARENT / "execution.json") ==
                       contract["pins"]["parent_execution_sha256"], "parent-execution-pin")
        node_source = file_sha(NODE_RECEIVER)
        python_source = file_sha(PYTHON_RECEIVER)
        campaign.check(node_source != python_source, "distinct-source-fingerprints")
        source_text = NODE_RECEIVER.read_text()
        campaign.check("child_process" not in source_text and "python" not in
                       " ".join(line for line in source_text.splitlines()
                                if line.startswith("import ")).lower(), "node-import-boundary")
        campaign.check(len(CASES) == 10, "case-count")

        for case_name, terminal_case in CASES:
            campaign.invoke(case_name, terminal_case, python_source, node_source)

        alpha_python = json.loads((PARENT / "cases" / "exact-alpha" / "receipt.json").read_bytes())
        alpha_node = json.loads((output / "cases" / "exact-alpha" / "node-receipt.json").read_bytes())
        changed_class = json.loads(canonical(alpha_node))
        changed_class["outcome"] = "UnknownContinuationState"
        changed_tuple = json.loads(canonical(alpha_node))
        changed_tuple["preserved_continuation"]["budget"]["spent_units"] = 8
        controls = {
            "classification-divergence": campaign.compare(
                alpha_python, changed_class, python_source, node_source),
            "preserved-tuple-divergence": campaign.compare(
                alpha_python, changed_tuple, python_source, node_source),
            "same-source-provenance": campaign.compare(
                alpha_python, alpha_node, python_source, python_source),
            "missing-second-result": campaign.compare(
                alpha_python, None, python_source, node_source),
        }
        campaign.check(all(value["outcome"] == "UnknownImplementationAgreement"
                           for value in controls.values()), "unknown-controls")
        for name, value in controls.items():
            campaign.save(output / "controls" / (name + ".json"), value)

        node_work = sum(int(record["node_work_units"]) for record in campaign.records)
        campaign.check(node_work <= 40_000, "total-node-work")
        campaign.check(campaign.comparison_units <= 1_000, "comparison-work")
        campaign.check(len(campaign.records) == 10, "complete-campaign")
        campaign.check(sum(record["node_outcome"] == "ContinuationReady"
                           for record in campaign.records) == 2, "ready-count")
        campaign.check(sum(record["node_outcome"] == "UnknownContinuationState"
                           for record in campaign.records) == 5, "unknown-count")
        campaign.check(sum(record["node_outcome"] == "InvalidEvidence"
                           for record in campaign.records) == 3, "invalid-count")

        child = resource.getrusage(resource.RUSAGE_CHILDREN)
        own = resource.getrusage(resource.RUSAGE_SELF)
        result = {
            "profile": "adva.research.continuation-resolution-crosscheck.execution.v0",
            "status": "Passed",
            "execution_kind": execution_kind,
            "node_timeout_seconds": timeout_seconds,
            "assertions": campaign.assertions,
            "node_processes": len(campaign.records),
            "python_receiver_processes": 0,
            "target_processes": 0,
            "search_candidates": 0,
            "implementation_correction_replays": 0,
            "node_work_units": node_work,
            "comparison_work_units": campaign.comparison_units,
            "node_seconds": campaign.node_seconds,
            "serialization_seconds": campaign.serialization_seconds,
            "whole_run_seconds": time.monotonic() - campaign.started,
            "max_child_rss_kib": child.ru_maxrss,
            "max_supervisor_rss_kib": own.ru_maxrss,
            "source_sha256": {
                "python_receiver": python_source,
                "node_receiver": node_source,
            },
            "cases": campaign.records,
            "controls": controls,
            "boundary": {
                "agreement_is_finite_implementation_comparison": True,
                "agreement_is_mathematical_truth": False,
                "disagreement_outcome": "UnknownImplementationAgreement",
                "fuel_delta": 0,
                "authorizes_continuation": False,
                "authorizes_effect": False,
                "authorizes_retry": False,
                "authorizes_refund": False,
                "native_authority": False,
                "free_authority": False,
                "new_vocabulary": [],
            },
        }
        campaign.save(output / "execution.json", result)
        print(canonical({key: value for key, value in result.items()
                         if key not in ("cases", "controls")} ).decode())
        return 0
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output.resolve()))
