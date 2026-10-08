#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import resource
import signal
import subprocess
import time


HERE = Path(__file__).resolve().parent
JAVA = HERE / "GenericConstructor.java"
PERL = HERE / "generic_constructor.pl"
SPEC = HERE / "third-instance.tsv"
CONTRACT = HERE / "contract.json"
PAYLOADS = (
    "continuation.json",
    "gate-query.json",
    "recovery-receipt.json",
    "resolution-query.json",
    "resolution-receipt.json",
    "source-pending.json",
    "terminal.json",
)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha(path: Path) -> str:
    return digest(path.read_bytes())


def read_spec() -> list[dict[str, str]]:
    lines = SPEC.read_text("ascii").splitlines()
    if lines[:2] != [
        "adva.research.continuation-abstract-instances.v0",
        "case_id\tattempt_id\tstate\tproblem_id\tinitial_units\tspent_units\tremaining_units",
    ] or len(lines) != 3:
        raise ValueError("ThirdInstanceShape")
    fields = lines[2].split("\t")
    if len(fields) != 7:
        raise ValueError("ThirdInstanceRow")
    return [dict(zip((
        "case_id", "attempt_id", "state", "problem_id",
        "initial_units", "spent_units", "remaining_units",
    ), fields, strict=True))]


class Campaign:
    def __init__(self, output: Path, contract: dict[str, object]) -> None:
        self.output = output
        self.contract = contract
        self.assertions = 0
        self.comparison_units = 0
        self.serialization_seconds = 0.0
        self.started = time.monotonic()

    def check(self, condition: bool, label: str) -> None:
        self.assertions += 1
        if not condition:
            raise AssertionError(label)

    def save(self, path: Path, value: object) -> None:
        started = time.monotonic()
        raw = canonical(value)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(raw)
            handle.flush()
        self.serialization_seconds += time.monotonic() - started

    def run_child(self, command: list[str], label: str) -> tuple[dict[str, object], float]:
        started = time.monotonic()
        completed = subprocess.run(
            command,
            cwd=HERE,
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=self.contract["limits"]["seconds_each"],
        )
        elapsed = time.monotonic() - started
        self.check(completed.returncode == 0, label + ":exit")
        self.check(len(completed.stdout) <=
                   self.contract["limits"]["stdout_bytes_each"], label + ":stdout")
        self.check(len(completed.stderr) <=
                   self.contract["limits"]["stderr_bytes_each"], label + ":stderr")
        self.check(completed.stderr == b"", label + ":silent-stderr")
        value = json.loads(completed.stdout)
        self.check(isinstance(value, dict), label + ":object-result")
        return value, elapsed

    def payload_map(self, root: Path, case_id: str) -> dict[str, bytes]:
        return {
            name: (root / case_id / name).read_bytes()
            for name in PAYLOADS if (root / case_id / name).is_file()
        }

    def compare(self, left: dict[str, bytes] | None, right: dict[str, bytes] | None,
                left_source: str, right_source: str) -> dict[str, object]:
        self.comparison_units += 1
        if left is None or right is None or left_source == right_source:
            return {"outcome": "UnknownImplementationAgreement",
                    "reason": "MissingOrSameSource", "compared_files": 0}
        self.comparison_units += len(left) + len(right)
        if set(left) != set(PAYLOADS) or set(right) != set(PAYLOADS):
            return {"outcome": "UnknownImplementationAgreement",
                    "reason": "CoverageDivergence", "compared_files": 0}
        compared = 0
        for path in PAYLOADS:
            self.comparison_units += 2
            try:
                left_value = json.loads(left[path])
                right_value = json.loads(right[path])
            except (json.JSONDecodeError, UnicodeDecodeError):
                return {"outcome": "UnknownImplementationAgreement",
                        "reason": "RepresentationDivergence",
                        "compared_files": compared}
            if canonical(left_value) != left[path] or canonical(right_value) != right[path]:
                return {"outcome": "UnknownImplementationAgreement",
                        "reason": "RepresentationDivergence",
                        "compared_files": compared}
            if left[path] != right[path]:
                return {"outcome": "UnknownImplementationAgreement",
                        "reason": "CanonicalByteDivergence",
                        "compared_files": compared}
            compared += 1
        return {"outcome": "ImplementationAgreement",
                "reason": "FiniteHeldOutConstructionMatch",
                "compared_files": compared}


def main(output: Path) -> int:
    if output.exists():
        raise SystemExit("output already exists")
    output.mkdir(parents=True)
    contract = json.loads(CONTRACT.read_bytes())
    campaign = Campaign(output, contract)
    signal.signal(signal.SIGALRM,
                  lambda *_: (_ for _ in ()).throw(TimeoutError("CampaignWallLimit")))
    signal.setitimer(signal.ITIMER_REAL, contract["limits"]["outer_seconds"])
    try:
        campaign.check(contract["status"] == "FrozenBeforeExecution", "contract-status")
        campaign.check(file_sha(JAVA) == contract["pins"]["java_constructor_sha256"],
                       "java-pin")
        campaign.check(file_sha(PERL) == contract["pins"]["perl_constructor_sha256"],
                       "perl-pin")
        campaign.check(file_sha(SPEC) == contract["pins"]["third_instance_sha256"],
                       "spec-pin")
        campaign.check(file_sha(Path(__file__)) == contract["pins"]["runner_sha256"],
                       "runner-pin")
        source_hashes = {file_sha(JAVA), file_sha(PERL)}
        campaign.check(len(source_hashes) == 2, "distinct-source-fingerprints")
        rows = read_spec()
        row = rows[0]
        campaign.check(int(row["initial_units"]) ==
                       int(row["spent_units"]) + int(row["remaining_units"]),
                       "third-instance-budget")
        source_texts = [JAVA.read_text("utf-8"), PERL.read_text("utf-8")]
        heldout_tokens = (row["case_id"], row["attempt_id"], row["problem_id"])
        campaign.check(all(token not in source for token in heldout_tokens
                           for source in source_texts),
                       "heldout-identifiers-absent-from-frozen-sources")
        campaign.check(contract["source_freeze_commit"] ==
                       "3c448a2358f8ab3a325b9fe7ea28f1b4d9ae6b6c",
                       "source-freeze-coordinate")

        java_output = output / "java"
        perl_output = output / "perl"
        campaign.check(not java_output.exists() and not perl_output.exists(),
                       "fresh-constructor-outputs")
        java_result, java_seconds = campaign.run_child([
            "java", "-Xmx64m", str(JAVA), "--spec", str(SPEC),
            "--output", str(java_output),
        ], "java")
        campaign.check(not perl_output.exists(), "java-before-perl-output")
        perl_result, perl_seconds = campaign.run_child([
            "perl", str(PERL), "--spec", str(SPEC), "--output", str(perl_output),
        ], "perl")

        for label, result in (("java", java_result), ("perl", perl_result)):
            campaign.check(result.get("case_count") == 1, label + ":case-count")
            campaign.check(result.get("files_written") == 8, label + ":file-count")
            campaign.check(result.get("abstract_spec_sha256") == file_sha(SPEC),
                           label + ":spec-coordinate")
            campaign.check(result.get("receiver_classification_supplied") is False,
                           label + ":no-answer")
            campaign.check(result.get("receiver_source_imported") is False,
                           label + ":no-receiver")
            work = result.get("work_units")
            campaign.check(type(work) is int and 0 <= work <=
                           contract["limits"][label + "_constructor_work_units"],
                           label + ":work")

        case_id = row["case_id"]
        java_payloads = campaign.payload_map(java_output, case_id)
        perl_payloads = campaign.payload_map(perl_output, case_id)
        comparison = campaign.compare(
            java_payloads, perl_payloads, file_sha(JAVA), file_sha(PERL))
        campaign.check(comparison["outcome"] == "ImplementationAgreement",
                       "third-instance-agreement")
        campaign.check(comparison["compared_files"] == 7, "complete-comparison")

        changed = dict(perl_payloads)
        changed_value = json.loads(changed["terminal.json"])
        changed_value["state"] = "cancelled"
        changed["terminal.json"] = canonical(changed_value)
        missing = dict(perl_payloads)
        del missing["gate-query.json"]
        noncanonical = dict(perl_payloads)
        noncanonical["source-pending.json"] += b"\n"
        controls = {
            "canonical-byte-divergence": campaign.compare(
                java_payloads, changed, file_sha(JAVA), file_sha(PERL)),
            "coverage-divergence": campaign.compare(
                java_payloads, missing, file_sha(JAVA), file_sha(PERL)),
            "representation-divergence": campaign.compare(
                java_payloads, noncanonical, file_sha(JAVA), file_sha(PERL)),
            "same-source-provenance": campaign.compare(
                java_payloads, perl_payloads, file_sha(JAVA), file_sha(JAVA)),
        }
        campaign.check(all(value["outcome"] == "UnknownImplementationAgreement"
                           for value in controls.values()), "unknown-controls")
        for name, value in controls.items():
            campaign.save(output / "controls" / (name + ".json"), value)

        campaign.check(campaign.comparison_units <=
                       contract["limits"]["comparison_work_units_total"],
                       "comparison-work")
        child = resource.getrusage(resource.RUSAGE_CHILDREN)
        own = resource.getrusage(resource.RUSAGE_SELF)
        result = {
            "profile": "adva.research.continuation-constructor-generalization.execution.v0",
            "status": "Passed",
            "assertions": campaign.assertions,
            "source_freeze_commit": contract["source_freeze_commit"],
            "java_constructor_processes": 1,
            "perl_constructor_processes": 1,
            "receiver_processes": 0,
            "target_processes": 0,
            "search_candidates": 0,
            "implementation_correction_replays": 0,
            "java_work_units": java_result["work_units"],
            "perl_work_units": perl_result["work_units"],
            "comparison_work_units": campaign.comparison_units,
            "java_seconds": java_seconds,
            "perl_seconds": perl_seconds,
            "serialization_seconds": campaign.serialization_seconds,
            "whole_run_seconds": time.monotonic() - campaign.started,
            "max_child_rss_kib": child.ru_maxrss,
            "max_supervisor_rss_kib": own.ru_maxrss,
            "third_instance": {
                "case_id": case_id,
                "state": row["state"],
                "budget": [
                    int(row["initial_units"]), int(row["spent_units"]),
                    int(row["remaining_units"]),
                ],
                "identifiers_absent_from_frozen_sources": True,
            },
            "source_sha256": {
                "java_constructor": file_sha(JAVA),
                "perl_constructor": file_sha(PERL),
                "third_instance": file_sha(SPEC),
            },
            "comparison": comparison,
            "controls": controls,
            "payload_sha256": {
                name: digest(raw) for name, raw in sorted(java_payloads.items())
            },
            "boundary": {
                "sources_frozen_before_third_instance_commit": True,
                "third_instance_supplies_expected_classification": False,
                "agreement_is_finite_constructor_generalization": True,
                "agreement_is_receipt_truth": False,
                "agreement_is_mathematical_truth": False,
                "disagreement_outcome": "UnknownImplementationAgreement",
                "fuel_delta": 0,
                "authorizes_continuation": False,
                "authorizes_effect": False,
                "native_authority": False,
                "free_authority": False,
                "new_vocabulary": [],
            },
        }
        campaign.save(output / "execution.json", result)
        print(canonical({key: value for key, value in result.items()
                         if key not in ("payload_sha256", "controls")}).decode())
        return 0
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output.resolve()))
