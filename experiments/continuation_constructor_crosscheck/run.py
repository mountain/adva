#!/usr/bin/env python3
"""Compare a Java constructor from abstract input with the frozen Perl constructor."""

from __future__ import annotations

import argparse
import csv
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
ABSTRACT = HERE / "abstract-instances.tsv"
JAVA = HERE / "Constructor.java"
PERL = ROOT / "experiments" / "continuation_resolution_heldout" / "constructor.pl"
CASE_IDS = ("rho", "tau")
PAYLOADS = (
    "continuation.json", "gate-query.json", "recovery-receipt.json",
    "resolution-query.json", "resolution-receipt.json", "source-pending.json",
    "terminal.json",
)


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


def abstract_rows() -> list[dict[str, str]]:
    lines = ABSTRACT.read_text(encoding="ascii").splitlines()
    if lines[0] != "adva.research.continuation-abstract-instances.v0":
        raise RuntimeError("AbstractProfile")
    return list(csv.DictReader(lines[1:], delimiter="\t"))


class Campaign:
    def __init__(self, output: Path, contract: dict[str, object]) -> None:
        self.output = output
        self.contract = contract
        self.started = time.monotonic()
        self.assertions = 0
        self.comparison_units = 0
        self.java_seconds = 0.0
        self.perl_seconds = 0.0
        self.serialization_seconds = 0.0

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

    def payload_map(self, root: Path) -> dict[str, bytes]:
        return {
            f"{case_id}/{name}": (root / case_id / name).read_bytes()
            for case_id in CASE_IDS for name in PAYLOADS
            if (root / case_id / name).is_file()
        }

    def compare(self, left: dict[str, bytes] | None, right: dict[str, bytes] | None,
                left_source: str, right_source: str) -> dict[str, object]:
        self.comparison_units += 1
        if left is None or right is None or left_source == right_source:
            return {"outcome": "UnknownImplementationAgreement",
                    "reason": "MissingOrSameSource", "compared_files": 0}
        expected = {f"{case_id}/{name}" for case_id in CASE_IDS for name in PAYLOADS}
        self.comparison_units += len(left) + len(right)
        if set(left) != expected or set(right) != expected:
            return {"outcome": "UnknownImplementationAgreement",
                    "reason": "CoverageDivergence", "compared_files": 0}
        compared = 0
        for path in sorted(expected):
            self.comparison_units += 2
            try:
                left_value = json.loads(left[path])
                right_value = json.loads(right[path])
            except (json.JSONDecodeError, UnicodeDecodeError):
                return {"outcome": "UnknownImplementationAgreement",
                        "reason": "RepresentationDivergence", "compared_files": compared}
            if canonical(left_value) != left[path] or canonical(right_value) != right[path]:
                return {"outcome": "UnknownImplementationAgreement",
                        "reason": "RepresentationDivergence", "compared_files": compared}
            if left[path] != right[path]:
                return {"outcome": "UnknownImplementationAgreement",
                        "reason": "CanonicalByteDivergence", "compared_files": compared}
            compared += 1
        return {"outcome": "ImplementationAgreement",
                "reason": "FiniteIndependentConstructionMatch", "compared_files": compared}


def main(output: Path) -> int:
    if output.exists():
        raise SystemExit("output already exists")
    output.mkdir(parents=True)
    contract = json.loads((HERE / "correction-contract.json").read_bytes())
    campaign = Campaign(output, contract)
    signal.signal(signal.SIGALRM,
                  lambda *_: (_ for _ in ()).throw(TimeoutError("CampaignWallLimit")))
    signal.setitimer(signal.ITIMER_REAL, contract["limits"]["outer_seconds"])
    try:
        campaign.check(contract["status"] == "FrozenCorrectionBeforeExecution",
                       "contract-status")
        campaign.check(file_sha(JAVA) == contract["pins"]["java_constructor_sha256"],
                       "java-pin")
        campaign.check(file_sha(PERL) == contract["pins"]["perl_constructor_sha256"],
                       "perl-pin")
        campaign.check(file_sha(ABSTRACT) == contract["pins"]["abstract_spec_sha256"],
                       "abstract-pin")
        campaign.check(file_sha(Path(__file__)) == contract["pins"]["runner_sha256"],
                       "runner-pin")
        sources = {file_sha(JAVA), file_sha(PERL)}
        campaign.check(len(sources) == 2, "distinct-source-fingerprints")
        java_text = JAVA.read_text()
        campaign.check("constructor.pl" not in java_text, "java:no-perl-source")

        rows = abstract_rows()
        campaign.check([row["case_id"] for row in rows] == list(CASE_IDS),
                       "abstract:case-order")
        campaign.check(all(int(row["initial_units"]) == int(row["spent_units"]) +
                           int(row["remaining_units"]) for row in rows),
                       "abstract:budgets")

        java_output = output / "java"
        perl_output = output / "perl"
        campaign.check(not perl_output.exists(), "java-before-perl")
        java_result, campaign.java_seconds = campaign.run_child([
            "java", "-Xmx64m", str(JAVA), "--spec", str(ABSTRACT),
            "--output", str(java_output),
        ], "java")
        campaign.check(not perl_output.exists(), "java-cannot-read-perl-output")
        perl_result, campaign.perl_seconds = campaign.run_child([
            "perl", str(PERL), "--output", str(perl_output),
        ], "perl")

        for label, result in (("java", java_result), ("perl", perl_result)):
            campaign.check(result.get("case_count") == len(CASE_IDS), label + ":case-count")
            campaign.check(result.get("files_written") == 15, label + ":file-count")
            campaign.check(result.get("receiver_classification_supplied") is False,
                           label + ":no-answer")
            campaign.check(result.get("receiver_source_imported") is False,
                           label + ":no-receiver")
            campaign.check(type(result.get("work_units")) is int and
                           0 <= result["work_units"] <=
                           contract["limits"][label + "_constructor_work_units"],
                           label + ":work")
        campaign.check(java_result.get("perl_output_read") is False,
                       "java:reports-no-perl-output")
        campaign.check(java_result.get("abstract_spec_sha256") == file_sha(ABSTRACT),
                       "java:abstract-coordinate")

        java_payloads = campaign.payload_map(java_output)
        perl_payloads = campaign.payload_map(perl_output)
        comparison = campaign.compare(
            java_payloads, perl_payloads, file_sha(JAVA), file_sha(PERL))
        campaign.check(comparison["outcome"] == "ImplementationAgreement",
                       "construction-agreement")
        campaign.check(comparison["compared_files"] == 14, "complete-comparison")

        changed = dict(perl_payloads)
        changed_key = "rho/terminal.json"
        changed_value = json.loads(changed[changed_key])
        changed_value["state"] = "cancelled"
        changed[changed_key] = canonical(changed_value)
        missing = dict(perl_payloads)
        del missing["tau/gate-query.json"]
        noncanonical = dict(perl_payloads)
        noncanonical["rho/source-pending.json"] += b"\n"
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
            "profile": "adva.research.continuation-constructor-crosscheck.execution.v0",
            "status": "Passed",
            "assertions": campaign.assertions,
            "java_constructor_processes": 1,
            "perl_constructor_processes": 1,
            "receiver_processes": 0,
            "target_processes": 0,
            "search_candidates": 0,
            "implementation_correction_replays": 0,
            "java_work_units": java_result["work_units"],
            "perl_work_units": perl_result["work_units"],
            "comparison_work_units": campaign.comparison_units,
            "java_seconds": campaign.java_seconds,
            "perl_seconds": campaign.perl_seconds,
            "serialization_seconds": campaign.serialization_seconds,
            "whole_run_seconds": time.monotonic() - campaign.started,
            "max_child_rss_kib": child.ru_maxrss,
            "max_supervisor_rss_kib": own.ru_maxrss,
            "source_sha256": {
                "abstract_spec": file_sha(ABSTRACT),
                "java_constructor": file_sha(JAVA),
                "perl_constructor": file_sha(PERL),
            },
            "comparison": comparison,
            "controls": controls,
            "payload_sha256": {
                path: digest(raw) for path, raw in sorted(java_payloads.items())
            },
            "boundary": {
                "java_ran_before_perl_output_existed": True,
                "java_reads_only_declared_abstract_spec": True,
                "expected_classification_supplied": False,
                "agreement_is_finite_constructor_comparison": True,
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
