#!/usr/bin/env python3
"""Run a held-out constructor through both continuation gate receivers."""

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
CONSTRUCTOR = HERE / "constructor.pl"
PYTHON_RECEIVER = ROOT / "experiments" / "continuation_resolution_gate" / "receiver.py"
NODE_RECEIVER = ROOT / "experiments" / "continuation_resolution_crosscheck" / "receiver.mjs"
CASE_IDS = ("rho", "tau")
TRIAD = {"ContinuationReady", "UnknownContinuationState", "InvalidEvidence"}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha(path: Path) -> str:
    return digest(path.read_bytes())


def atomic_write_new(path: Path, value: object | bytes) -> float:
    started = time.monotonic()
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
    return time.monotonic() - started


class Campaign:
    def __init__(self, output: Path, contract: dict[str, object]) -> None:
        self.output = output
        self.contract = contract
        self.started = time.monotonic()
        self.assertions = 0
        self.comparison_units = 0
        self.constructor_seconds = 0.0
        self.python_seconds = 0.0
        self.node_seconds = 0.0
        self.serialization_seconds = 0.0
        self.records: list[dict[str, object]] = []

    def check(self, condition: bool, label: str) -> None:
        self.assertions += 1
        if not condition:
            raise RuntimeError("CheckFailed:" + label)

    def save(self, path: Path, value: object | bytes) -> None:
        self.serialization_seconds += atomic_write_new(path, value)

    def run_child(self, command: list[str], label: str) -> tuple[dict[str, object], float]:
        started = time.monotonic()
        completed = subprocess.run(
            command,
            capture_output=True,
            timeout=self.contract["limits"]["seconds_each"],
            check=False,
        )
        elapsed = time.monotonic() - started
        self.check(completed.returncode == 0, label + ":exit")
        self.check(len(completed.stdout) <= self.contract["limits"]["stdout_bytes_each"],
                   label + ":stdout")
        self.check(len(completed.stderr) <= self.contract["limits"]["stderr_bytes_each"],
                   label + ":stderr")
        self.check(completed.stderr == b"", label + ":silent-stderr")
        value = json.loads(completed.stdout)
        self.check(isinstance(value, dict), label + ":object-result")
        return value, elapsed

    def compare(self, python: dict[str, object] | None, node: dict[str, object] | None,
                python_source: str, node_source: str) -> dict[str, str]:
        self.comparison_units += 1
        if python is None or node is None or python_source == node_source:
            return {"outcome": "UnknownImplementationAgreement", "reason": "MissingOrSameSource"}
        self.comparison_units += 2
        if python.get("outcome") != node.get("outcome"):
            return {"outcome": "UnknownImplementationAgreement", "reason": "ClassificationDivergence"}
        self.comparison_units += 1
        if canonical(python.get("preserved_continuation")) != \
                canonical(node.get("preserved_continuation")):
            return {"outcome": "UnknownImplementationAgreement", "reason": "PreservedTupleDivergence"}
        return {"outcome": "ImplementationAgreement", "reason": "FiniteHeldOutProjectionMatch"}

    def construct(self) -> dict[str, object]:
        constructed = self.output / "constructed"
        result, elapsed = self.run_child(
            ["perl", str(CONSTRUCTOR), "--output", str(constructed)], "constructor")
        self.constructor_seconds += elapsed
        self.check(result["case_count"] == len(CASE_IDS), "constructor:case-count")
        self.check(result["files_written"] == len(CASE_IDS) * 7 + 1,
                   "constructor:file-count")
        self.check(result["receiver_classification_supplied"] is False,
                   "constructor:no-classification")
        self.check(result["receiver_source_imported"] is False,
                   "constructor:no-receiver-import")
        self.check(type(result["work_units"]) is int and
                   0 <= result["work_units"] <= self.contract["limits"]["constructor_work_units"],
                   "constructor:work")
        manifest = json.loads((constructed / "manifest.json").read_bytes())
        self.check(manifest["case_count"] == len(CASE_IDS), "manifest:case-count")
        self.check([case["case_id"] for case in manifest["cases"]] == list(CASE_IDS),
                   "manifest:case-order")
        self.check(all(set(case) == {"case_id", "input_sha256"}
                       for case in manifest["cases"]), "manifest:no-answer-field")
        return result

    def receive_case(self, case_id: str, python_source: str, node_source: str) -> None:
        directory = self.output / "constructed" / case_id
        query = directory / "gate-query.json"
        continuation = directory / "continuation.json"
        resolution = directory / "resolution-receipt.json"
        selected = tuple(sorted(directory.glob("*.json")))
        before = {path.name: file_sha(path) for path in selected}

        python_receipt, python_elapsed = self.run_child([
            "python", "-O", str(PYTHON_RECEIVER), "--query", str(query),
            "--continuation", str(continuation), "--resolution-receipt", str(resolution),
        ], case_id + ":python")
        self.python_seconds += python_elapsed
        node_receipt, node_elapsed = self.run_child([
            "node", "--max-old-space-size=32", str(NODE_RECEIVER), "--query", str(query),
            "--continuation", str(continuation), "--resolution-receipt", str(resolution),
        ], case_id + ":node")
        self.node_seconds += node_elapsed

        after = {path.name: file_sha(path) for path in selected}
        self.check(before == after, case_id + ":input-preservation")
        self.check(python_receipt.get("outcome") in TRIAD, case_id + ":python-triad")
        self.check(node_receipt.get("outcome") in TRIAD, case_id + ":node-triad")
        continuation_value = json.loads(continuation.read_bytes())
        self.check(canonical(python_receipt.get("preserved_continuation")) ==
                   canonical(continuation_value), case_id + ":python-preserves-tuple")
        self.check(canonical(node_receipt.get("preserved_continuation")) ==
                   canonical(continuation_value), case_id + ":node-preserves-tuple")
        for implementation, receipt in (("python", python_receipt), ("node", node_receipt)):
            self.check(receipt.get("fuel_delta") == 0, case_id + f":{implementation}:fuel")
            self.check(receipt.get("target_processes") == 0,
                       case_id + f":{implementation}:targets")
            self.check(all(receipt.get(key) is False for key in (
                "effect_authority", "retry_authority", "refund_authority",
                "mutation_authority", "native_authority", "free_authority",
            )), case_id + f":{implementation}:authority")
        comparison = self.compare(python_receipt, node_receipt, python_source, node_source)
        self.check(comparison["outcome"] == "ImplementationAgreement",
                   case_id + ":agreement")
        python_work = python_receipt.get("work_units")
        node_work = node_receipt.get("work_units")
        self.check(type(python_work) is int and python_work >= 0, case_id + ":python-work")
        self.check(type(node_work) is int and node_work >= 0, case_id + ":node-work")
        self.save(self.output / "receipts" / case_id / "python.json", python_receipt)
        self.save(self.output / "receipts" / case_id / "node.json", node_receipt)
        self.save(self.output / "receipts" / case_id / "comparison.json", comparison)
        self.records.append({
            "case_id": case_id,
            "observed_python_outcome": python_receipt["outcome"],
            "observed_node_outcome": node_receipt["outcome"],
            "comparison": comparison,
            "python_work_units": python_work,
            "node_work_units": node_work,
            "python_seconds": python_elapsed,
            "node_seconds": node_elapsed,
            "input_sha256_before": before,
            "input_sha256_after": after,
        })


def main(output: Path) -> int:
    if output.exists():
        raise SystemExit("output already exists")
    output.mkdir(parents=True)
    contract = json.loads((HERE / "contract.json").read_bytes())
    campaign = Campaign(output, contract)
    signal.signal(signal.SIGALRM,
                  lambda *_: (_ for _ in ()).throw(TimeoutError("CampaignWallLimit")))
    signal.setitimer(signal.ITIMER_REAL, contract["limits"]["outer_seconds"])
    try:
        campaign.check(contract["status"] == "FrozenBeforeExecution", "contract-status")
        campaign.check(file_sha(CONSTRUCTOR) == contract["pins"]["constructor_sha256"],
                       "constructor-pin")
        campaign.check(file_sha(PYTHON_RECEIVER) == contract["pins"]["python_receiver_sha256"],
                       "python-pin")
        campaign.check(file_sha(NODE_RECEIVER) == contract["pins"]["node_receiver_sha256"],
                       "node-pin")
        sources = {file_sha(path) for path in (CONSTRUCTOR, PYTHON_RECEIVER, NODE_RECEIVER)}
        campaign.check(len(sources) == 3, "distinct-source-fingerprints")
        constructor_text = CONSTRUCTOR.read_text()
        campaign.check("receiver.py" not in constructor_text and "receiver.mjs" not in constructor_text,
                       "constructor-import-boundary")
        constructor_result = campaign.construct()

        python_source = file_sha(PYTHON_RECEIVER)
        node_source = file_sha(NODE_RECEIVER)
        for case_id in CASE_IDS:
            campaign.receive_case(case_id, python_source, node_source)

        first_python = json.loads((output / "receipts" / CASE_IDS[0] / "python.json").read_bytes())
        first_node = json.loads((output / "receipts" / CASE_IDS[0] / "node.json").read_bytes())
        changed_class = json.loads(canonical(first_node))
        changed_class["outcome"] = next(value for value in TRIAD
                                        if value != first_node["outcome"])
        changed_tuple = json.loads(canonical(first_node))
        changed_tuple["preserved_continuation"]["budget"]["spent_units"] += 1
        controls = {
            "classification-divergence": campaign.compare(
                first_python, changed_class, python_source, node_source),
            "preserved-tuple-divergence": campaign.compare(
                first_python, changed_tuple, python_source, node_source),
            "same-source-provenance": campaign.compare(
                first_python, first_node, python_source, python_source),
            "missing-second-result": campaign.compare(
                first_python, None, python_source, node_source),
        }
        campaign.check(all(value["outcome"] == "UnknownImplementationAgreement"
                           for value in controls.values()), "unknown-controls")
        for name, value in controls.items():
            campaign.save(output / "controls" / (name + ".json"), value)

        receiver_work = sum(int(record["python_work_units"]) +
                            int(record["node_work_units"]) for record in campaign.records)
        campaign.check(receiver_work <= contract["limits"]["receiver_work_units_total"],
                       "receiver-work")
        campaign.check(campaign.comparison_units <=
                       contract["limits"]["comparison_work_units_total"],
                       "comparison-work")
        campaign.check(len(campaign.records) == len(CASE_IDS), "complete-campaign")

        child = resource.getrusage(resource.RUSAGE_CHILDREN)
        own = resource.getrusage(resource.RUSAGE_SELF)
        result = {
            "profile": "adva.research.continuation-resolution-heldout.execution.v0",
            "status": "Passed",
            "assertions": campaign.assertions,
            "constructor_processes": 1,
            "python_receiver_processes": len(CASE_IDS),
            "node_receiver_processes": len(CASE_IDS),
            "target_processes": 0,
            "search_candidates": 0,
            "implementation_correction_replays": 0,
            "constructor_work_units": constructor_result["work_units"],
            "receiver_work_units": receiver_work,
            "comparison_work_units": campaign.comparison_units,
            "constructor_seconds": campaign.constructor_seconds,
            "python_seconds": campaign.python_seconds,
            "node_seconds": campaign.node_seconds,
            "serialization_seconds": campaign.serialization_seconds,
            "whole_run_seconds": time.monotonic() - campaign.started,
            "max_child_rss_kib": child.ru_maxrss,
            "max_supervisor_rss_kib": own.ru_maxrss,
            "source_sha256": {
                "constructor": file_sha(CONSTRUCTOR),
                "python_receiver": python_source,
                "node_receiver": node_source,
            },
            "cases": campaign.records,
            "controls": controls,
            "boundary": {
                "constructor_supplies_expected_classification": False,
                "comparator_supplies_expected_classification": False,
                "agreement_is_finite_heldout_implementation_comparison": True,
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
                         if key not in ("cases", "controls")}).decode())
        return 0
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output.resolve()))

