#!/usr/bin/env python3
"""Bounded byte-projection audit for the retained Research 0162 campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import resource
import sys
import time
from collections import defaultdict
from pathlib import Path

ROUND_RE = re.compile(
    r"^docs/research/0162-evidence/"
    r"(archive-cycle1|archive-cycle2|archive-cycle3|final-rounds)/"
    r"round-(\d{3})/(learn|run)-(\d{2})\.(transition|frontier)\.adva$"
)
CYCLES = ("archive-cycle1", "archive-cycle2", "archive-cycle3", "final-rounds")
EXPECTED_ROUNDS = 400
EXPECTED_PER_ROUND = 18
MAX_ENTRIES = 8000
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_OUTPUT_BYTES = 2 * 1024 * 1024


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("input exceeds byte bound")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("input root must be object")
    return value, raw


def coordinate(entry: dict) -> tuple[str, int, str, int, str]:
    if set(entry) != {"path", "oid", "size"}:
        raise ValueError("entry fields mismatch")
    if not isinstance(entry["size"], int) or entry["size"] < 0:
        raise ValueError("invalid size")
    if not isinstance(entry["oid"], str) or not re.fullmatch(r"[0-9a-f]{40}", entry["oid"]):
        raise ValueError("invalid Git blob OID")
    match = ROUND_RE.fullmatch(entry["path"])
    if match is None:
        raise ValueError("path outside projection")
    cycle, round_text, phase, slot_text, kind = match.groups()
    round_no, slot = int(round_text), int(slot_text)
    if round_no not in range(1, 101) or slot not in range(1, 7):
        raise ValueError("round or slot outside contract")
    if phase == "run" and kind != "transition":
        raise ValueError("run frontier is outside projection")
    return cycle, round_no, phase, slot, kind


def classify(entries: list[dict]) -> dict:
    if len(entries) > MAX_ENTRIES:
        return {"status": "RejectedMalformedIndex", "reason": "entry bound exceeded"}
    rounds: dict[tuple[str, int], list[tuple[str, int, str, str, int]]] = defaultdict(list)
    seen: set[tuple[str, int, str, int, str]] = set()
    group_oids: dict[str, set[str]] = defaultdict(set)
    try:
        for entry in entries:
            key = coordinate(entry)
            if key in seen:
                raise ValueError("duplicate normalized coordinate")
            seen.add(key)
            cycle, round_no, phase, slot, kind = key
            rounds[(cycle, round_no)].append((phase, slot, kind, entry["oid"], entry["size"]))
            group_oids[f"{phase}:{kind}:slot{slot}"].add(entry["oid"])
    except ValueError as error:
        return {"status": "RejectedMalformedIndex", "reason": str(error)}

    expected_round_keys = {(cycle, n) for cycle in CYCLES for n in range(1, 101)}
    missing_rounds = sorted(expected_round_keys - set(rounds))
    malformed_rounds = sorted(
        [list(key) for key, values in rounds.items() if len(values) != EXPECTED_PER_ROUND]
    )
    if missing_rounds or malformed_rounds or len(entries) != EXPECTED_ROUNDS * EXPECTED_PER_ROUND:
        return {
            "status": "UnknownCoverageGap",
            "reason": "projection coverage is not exact",
            "entry_count": len(entries),
            "round_count": len(rounds),
            "missing_round_count": len(missing_rounds),
            "malformed_round_count": len(malformed_rounds),
        }

    fingerprints = {}
    for key, values in rounds.items():
        normalized = sorted(values)
        fingerprints[f"{key[0]}:{key[1]:03d}"] = sha256_bytes(canonical(normalized))
    unique_fingerprints = sorted(set(fingerprints.values()))
    status = "EvidenceStutter" if len(unique_fingerprints) == 1 else "VariationObserved"
    return {
        "status": status,
        "reason": "all normalized round projections coincide" if status == "EvidenceStutter" else "at least two normalized round projections differ",
        "entry_count": len(entries),
        "round_count": len(rounds),
        "artifacts_per_round": EXPECTED_PER_ROUND,
        "unique_round_fingerprints": len(unique_fingerprints),
        "round_fingerprints": unique_fingerprints,
        "groups": {
            name: {"count": EXPECTED_ROUNDS, "distinct_blob_oids": len(oids), "oids": sorted(oids)}
            for name, oids in sorted(group_oids.items())
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, default=Path(__file__).with_name("input-index.json"))
    parser.add_argument("--contract", type=Path, default=Path(__file__).with_name("contract.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite output")

    resource.setrlimit(resource.RLIMIT_CPU, (8, 8))
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
    started = time.perf_counter_ns()
    index, index_raw = load_json(args.index)
    contract, contract_raw = load_json(args.contract)
    entries = index.get("entries")
    if not isinstance(entries, list):
        raise SystemExit("entries must be a list")

    actual = classify(entries)
    varied_entries = json.loads(json.dumps(entries))
    varied_entries[-1]["oid"] = "f" * 40
    reuse = classify(varied_entries)
    missing = classify(entries[:-1])
    duplicate = classify(entries + [dict(entries[-1])])
    controls = {
        "fresh_variation": reuse["status"] == "VariationObserved",
        "coverage_gap": missing["status"] == "UnknownCoverageGap",
        "duplicate_rejected": duplicate["status"] == "RejectedMalformedIndex",
    }
    passed = actual["status"] == "EvidenceStutter" and all(controls.values())
    elapsed_before_serialization = time.perf_counter_ns() - started
    saved_rounds = EXPECTED_ROUNDS - 2
    report = {
        "schema": "adva.evidence-stutter.evidence.v0",
        "version": 0,
        "status": "PassedFiniteCalibration" if passed else "FailedFiniteCalibration",
        "source_commit": index.get("source_commit"),
        "source_tree": index.get("source_tree"),
        "input_sha256": sha256_bytes(index_raw),
        "contract_sha256": sha256_bytes(contract_raw),
        "source_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "actual": actual,
        "controls": {"outcomes": controls, "variation": reuse, "missing": missing, "duplicate": duplicate},
        "comparison": {
            "without_word": {"protocol_completed_rounds": EXPECTED_ROUNDS},
            "with_evidence_stutter": {"baseline_rounds": 1, "stuttering_replays": EXPECTED_ROUNDS - 1, "variation_observed": 0},
            "counterfactual_stop_after_one_confirmation": {
                "rounds_not_launched": saved_rounds,
                "artifact_writes_not_requested": saved_rounds * EXPECTED_PER_ROUND,
                "child_launches_not_requested": saved_rounds * 12,
                "claim": "accounting only; not a measured runtime speedup"
            }
        },
        "cost": {
            "elapsed_before_serialization_ns": elapsed_before_serialization,
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "search_candidates": 0,
            "input_entries": len(entries),
            "output_size_is_not_peak_memory": True
        },
        "boundary": {
            "git_blob_oid_use": "exact identity in the pinned Git tree, not authentication or native semantic identity",
            "variation_is_only_necessary": "VariationObserved is not sufficient for learning",
            "omitted": ["JSON report timing", "absolute paths", "stdout/stderr emptiness", "external human inputs", "native semantics", "free"],
            "arithmetic_truth": "no additive-zero or multiplicative-identity judgment was made"
        }
    }
    encoded = json.dumps(report, indent=2, sort_keys=True).encode() + b"\n"
    if len(encoded) > MAX_OUTPUT_BYTES:
        raise SystemExit("output exceeds byte bound")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(encoded)
    print(json.dumps({"status": report["status"], "actual": actual["status"], "output_bytes": len(encoded)}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
