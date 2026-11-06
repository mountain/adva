#!/usr/bin/env python3
"""Read-only acceptance of the finished 2026-11-06 capture and static review."""
import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import subprocess
import sys

import inventory_pinned_machine_reference_ledger as capture

# Post-capture pins. Keep them outside the single-attempt contract and directory.
CONTRACT_SHA256 = "3130a81a4933af62cc35b2c980fe2fdd3cbc2f197f055c58524891c495eafe47"
RECEIPT_SHA256 = "3a0b97db6ae274f03503fe583b901608a88d0bb4c8b95aa9086dbb328e86f421"
SUPERVISOR_SHA256 = "f96909f0a7a542863cf0ba9ef086dcea485322ae8c94aca6edd11269fb9fc837"
REVIEW_SHA256 = "80f6762a7c7928b00a2ed013798772bea337342efed2a4d7c5e971339cc8dbbd"
REVIEW = capture.EXP / "machine-reference-ledger-review-20261106.json"


def check_completion(supervisor, receipt, contract):
    capture.require(supervisor["worker_status"] == "ExitedCleanly"
                    and type(supervisor["worker_exit"]) is int and supervisor["worker_exit"] == 0
                    and supervisor["timed_out"] is False, "worker did not finish cleanly")
    elapsed = supervisor["elapsed_ns"]
    search = receipt["search_and_write_ns"]
    preflight = receipt["preflight_ns"]
    readback = receipt["through_readback_ns"]
    capture.require(all(type(value) is int and value >= 0
                        for value in (elapsed, search, preflight, readback)), "invalid duration")
    capture.require(search <= contract["budget"]["search_wall_seconds_max"] * 10**9,
                    "search time exceeds contract")
    capture.require(elapsed <= contract["additional_limits"]["worker_wall_seconds_max"] * 10**9,
                    "supervisor time exceeds acceptance limit")
    capture.require(preflight + search <= readback <= elapsed, "inconsistent phase durations")


def verify_review(run=capture.RUN, review_file=REVIEW):
    anchor = capture.frozen_contract(CONTRACT_SHA256)
    receipt_hash = capture.verify(run, anchor, CONTRACT_SHA256)
    capture.require(receipt_hash == RECEIPT_SHA256, "receipt differs from reviewed capture")
    receipt = capture.load_json(run / "receipt.json")
    supervisor_bytes = capture.regular_bytes(run / "supervisor.json", 1_000_000)
    check_completion(json.loads(supervisor_bytes), receipt, capture.load_json(capture.CONTRACT))
    capture.require(capture.sha(supervisor_bytes) == SUPERVISOR_SHA256, "supervisor digest differs")
    expected_phase = {"contract_sha256": CONTRACT_SHA256, "phase": "receipt_commit"}
    capture.require(capture.regular_bytes(run / "phase.json", 4096) ==
                    capture.encode(expected_phase) + b"\n", "last phase differs")

    raw = capture.regular_bytes(review_file, 1_000_000)
    capture.require(capture.sha(raw) == REVIEW_SHA256, "static review digest differs")
    review = json.loads(raw)
    capture.require(review["contract_sha256"] == CONTRACT_SHA256
                    and review["receipt_sha256"] == receipt_hash
                    and review["ledger_sha256"] == receipt["ledger"]["sha256"]
                    and review["revision"] == receipt["machine_revision"], "review inputs differ")
    return review


def verify_locations(machine, review):
    """Check only saved hit coordinates against Git blobs, without running machine code."""
    manifest = {item["path"]: item for item in capture.load_json(capture.RUN / "manifest.json")}
    data = capture.regular_bytes(capture.RUN / "references.jsonl", capture.LEDGER_CAP)
    capture.require(capture.sha(data) == review["ledger_sha256"], "ledger changed before source check")
    by_path = defaultdict(list)
    for line in data.splitlines():
        row = json.loads(line)
        by_path[row["path"]].append(row)
    checked = 0
    for path, rows in by_path.items():
        blob = subprocess.check_output(
            ["git", "--no-replace-objects", "-C", str(machine), "cat-file", "blob",
             f"{review['revision']}:{path}"], timeout=10, stderr=subprocess.DEVNULL,
            env={**os.environ, "GIT_NO_LAZY_FETCH": "1"})
        entry = manifest[path]
        capture.require(len(blob) == entry["bytes"] and capture.sha(blob) == entry["sha256"],
                        f"file differs at {path}")
        lines = blob.decode("utf-8").splitlines()
        for row in rows:
            number = row["line"]
            capture.require(1 <= number <= len(lines), f"missing line at {path}:{number}")
            lowered = lines[number - 1].casefold()
            terms = [term for term in capture.prior.TERMS if term.casefold() in lowered]
            capture.require(terms == row["terms"], f"terms differ at {path}:{number}")
            checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine", type=Path, help="optional local Git repository containing pinned blobs")
    args = parser.parse_args()
    try:
        review = verify_review()
        report = {"static_decision": review["decision"], "reviewed": review["rows_reviewed"],
                  "receiver_outcomes": review["actual_receiver_outcomes"]}
        if args.machine is not None:
            report["coordinates_verified_at_pin"] = verify_locations(args.machine, review)
        print(json.dumps(report, sort_keys=True))
        return 0
    except (KeyError, TypeError, ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"Unknown: acceptance failed ({type(error).__name__})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
