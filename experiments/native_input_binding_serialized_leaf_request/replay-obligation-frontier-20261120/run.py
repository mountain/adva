#!/usr/bin/env python3
import copy
import hashlib
import json
import resource
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEPENDENCIES = (
    ("fixture.path", ("fixture", "path")),
    ("fixture.git_blob_sha1", ("fixture", "git_blob_sha1")),
    ("fixture.bytes", ("fixture", "bytes")),
    ("fixture.sha256", ("fixture", "sha256")),
    ("consumer.path", ("consumer", "path")),
    ("consumer.git_blob_sha1", ("consumer", "git_blob_sha1")),
    ("consumer.sha256", ("consumer", "sha256")),
    ("consumer.byte_budget", ("consumer", "byte_budget")),
    ("consumer.work_budget", ("consumer", "work_budget")),
    ("workflow.path", ("workflow", "path")),
    ("workflow.git_blob_sha1", ("workflow", "git_blob_sha1")),
)


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def get_path(value, path):
    cursor = value
    for key in path:
        cursor = cursor.get(key) if isinstance(cursor, dict) else None
    return cursor


def mutate(value, path, replacement):
    result = copy.deepcopy(value)
    cursor = result
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = replacement
    return result


def historical_valid(historical):
    if historical is None:
        return False
    return (
        historical.get("workflow", {}).get("conclusion") == "success"
        and historical.get("case") == "matching"
        and historical.get("consumer_outcome") == "AcceptedCurrentFixture"
        and historical.get("native_outcome") == "SuccessorVerified"
    )


def evaluate(historical, current):
    if not historical_valid(historical):
        return {
            "status": "Refused/HistoricalAcceptanceInvalid",
            "frontier": [],
            "current_acceptance": "NotEstablished",
        }
    if current is None:
        return {
            "status": "CertificateObstruction/MissingCurrentSnapshot",
            "frontier": ["current_snapshot"],
            "current_acceptance": "NotEstablished",
        }
    if historical.get("repository") != current.get("repository"):
        return {
            "status": "Refused/RepositoryMismatch",
            "frontier": ["repository"],
            "current_acceptance": "NotEstablished",
        }
    frontier = [name for name, path in DEPENDENCIES if get_path(historical, path) != get_path(current, path)]
    if frontier:
        status = "ReplayRequired/DependencyDrift"
    else:
        status = "ContinuityChecked/HistoricalEvidenceReusable"
    return {
        "status": status,
        "frontier": frontier,
        "snapshot_commit_changed": historical.get("commit") != current.get("commit"),
        "current_acceptance": "NotEstablished",
    }


def historical_only(historical, _current):
    return (
        "HistoricalOnly/AcceptedAtPinnedRun"
        if historical_valid(historical)
        else "HistoricalOnly/Invalid"
    )


def main():
    started = time.perf_counter_ns()
    historical = json.loads((ROOT / "historical-evidence.json").read_text())
    current = json.loads((ROOT / "current-snapshot.json").read_text())
    constructed = time.perf_counter_ns()

    fresh_historical = copy.deepcopy(historical)
    fresh_historical.update({"repository": "synthetic/fresh", "commit": "a" * 40})
    fresh_current = copy.deepcopy(current)
    fresh_current.update({"repository": "synthetic/fresh", "commit": "b" * 40, "ref": "trunk"})
    fresh_historical["fixture"]["git_blob_sha1"] = "1" * 40
    fresh_current["fixture"]["git_blob_sha1"] = "1" * 40
    fresh_historical["consumer"]["git_blob_sha1"] = "2" * 40
    fresh_current["consumer"]["git_blob_sha1"] = "2" * 40
    fresh_historical["workflow"]["git_blob_sha1"] = "3" * 40
    fresh_current["workflow"]["git_blob_sha1"] = "3" * 40

    failed_historical = mutate(historical, ("workflow", "conclusion"), "failure")
    fresh_multi_drift = mutate(fresh_current, ("consumer", "git_blob_sha1"), "4" * 40)
    fresh_multi_drift = mutate(fresh_multi_drift, ("workflow", "git_blob_sha1"), "5" * 40)
    cases = [
        ("canonical-current", historical, current),
        ("fixture-drift", historical, mutate(current, ("fixture", "git_blob_sha1"), "0" * 40)),
        ("consumer-drift", historical, mutate(current, ("consumer", "git_blob_sha1"), "0" * 40)),
        ("workflow-drift", historical, mutate(current, ("workflow", "git_blob_sha1"), "0" * 40)),
        ("byte-budget-drift", historical, mutate(current, ("consumer", "byte_budget"), 65535)),
        ("work-budget-drift", historical, mutate(current, ("consumer", "work_budget"), 511)),
        ("missing-current", historical, None),
        ("failed-historical", failed_historical, current),
        ("fresh-exact", fresh_historical, fresh_current),
        ("fresh-multi-drift", fresh_historical, fresh_multi_drift),
    ]
    rows = []
    for name, left, right in cases:
        explicit = evaluate(left, right)
        rows.append({
            "name": name,
            "historical_only": historical_only(left, right),
            "explicit_frontier": explicit,
        })
    verified = time.perf_counter_ns()

    expected = {
        "canonical-current": ("ContinuityChecked/HistoricalEvidenceReusable", []),
        "fixture-drift": ("ReplayRequired/DependencyDrift", ["fixture.git_blob_sha1"]),
        "consumer-drift": ("ReplayRequired/DependencyDrift", ["consumer.git_blob_sha1"]),
        "workflow-drift": ("ReplayRequired/DependencyDrift", ["workflow.git_blob_sha1"]),
        "byte-budget-drift": ("ReplayRequired/DependencyDrift", ["consumer.byte_budget"]),
        "work-budget-drift": ("ReplayRequired/DependencyDrift", ["consumer.work_budget"]),
        "missing-current": ("CertificateObstruction/MissingCurrentSnapshot", ["current_snapshot"]),
        "failed-historical": ("Refused/HistoricalAcceptanceInvalid", []),
        "fresh-exact": ("ContinuityChecked/HistoricalEvidenceReusable", []),
        "fresh-multi-drift": (
            "ReplayRequired/DependencyDrift",
            ["consumer.git_blob_sha1", "workflow.git_blob_sha1"],
        ),
    }
    actual = {
        row["name"]: (
            row["explicit_frontier"]["status"],
            row["explicit_frontier"]["frontier"],
        )
        for row in rows
    }
    false_coalescences = sum(
        row["historical_only"] == "HistoricalOnly/AcceptedAtPinnedRun"
        and row["explicit_frontier"]["status"] != "ContinuityChecked/HistoricalEvidenceReusable"
        for row in rows
    )
    checks = {
        "all_expected": actual == expected,
        "false_coalescences_under_historical_only": false_coalescences,
        "canonical_commit_changed_but_frontier_empty": (
            rows[0]["explicit_frontier"]["snapshot_commit_changed"]
            and not rows[0]["explicit_frontier"]["frontier"]
        ),
        "never_current_acceptance": all(
            row["explicit_frontier"]["current_acceptance"] == "NotEstablished"
            and "AcceptedNow" not in row["explicit_frontier"]["status"]
            for row in rows
        ),
    }
    if not all((checks["all_expected"], checks["canonical_commit_changed_but_frontier_empty"], checks["never_current_acceptance"])):
        raise AssertionError({"expected": expected, "actual": actual, "checks": checks})

    baseline_form = {
        "run_id": historical["workflow"]["run_id"],
        "job_id": historical["workflow"]["job_id"],
        "outcome": historical["native_outcome"],
    }
    explicit_form = {
        "historical_commit": historical["commit"],
        "current_commit": current["commit"],
        "dependencies": {name: get_path(current, path) for name, path in DEPENDENCIES},
        "frontier": rows[0]["explicit_frontier"]["frontier"],
        "current_acceptance": "NotEstablished",
    }
    formation_started = time.perf_counter_ns()
    baseline_bytes = canonical_bytes(baseline_form)
    baseline_formation_ns = time.perf_counter_ns() - formation_started
    formation_started = time.perf_counter_ns()
    explicit_bytes = canonical_bytes(explicit_form)
    explicit_formation_ns = time.perf_counter_ns() - formation_started

    outcome = {
        "schema": "adva.research.replay-obligation-frontier.outcome.v0",
        "status": "PassedBoundedReplayObligationFrontier",
        "claim": "Current main preserves the pinned fixture, consumer, workflow and budgets of the historical native run, so its replay-obligation frontier is empty; current native acceptance remains NotEstablished.",
        "instances": rows,
        "checks": checks,
        "comparison": {
            "baseline_formation_ns": baseline_formation_ns,
            "baseline_bytes": len(baseline_bytes),
            "explicit_formation_ns": explicit_formation_ns,
            "explicit_bytes": len(explicit_bytes),
            "formation_byte_delta": len(explicit_bytes) - len(baseline_bytes),
            "claim_boundary": "The explicit form distinguishes these ten cases; no global expressivity or efficiency theorem is claimed."
        },
        "cost": {
            "routes": 1,
            "counted_cases": len(rows),
            "search_candidates": 0,
            "construction_ns": constructed - started,
            "evaluation_and_verification_ns": verified - constructed,
            "serialization_ns": None,
            "serialized_bytes": None,
            "ru_maxrss_kib_before_serialization": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "implementation_correction_replays": 0,
            "native_executions": 0,
        },
        "proposed_word": {
            "word": "replay-obligation frontier",
            "state": "Proposed",
            "role": "name the exact finite dependency coordinates that must be revalidated or replayed before historical acceptance can inform a changed current snapshot",
            "input": "pinned historical native evidence and a current snapshot of fixture, consumer, workflow and byte/work budgets",
            "output_relation": "ContinuityChecked/HistoricalEvidenceReusable with an empty frontier, ReplayRequired/DependencyDrift with an ordered frontier, or a refusal/obstruction",
            "applicability": "historical acceptance is valid and both records use the same repository and declared dependency family",
            "witness": "eight canonical controls plus one fresh exact and one fresh two-coordinate drift reuse",
            "refusal_conditions": [
                "historical workflow, case, consumer outcome or native outcome is not successful",
                "repository differs",
                "current snapshot is missing"
            ],
            "expansion": "verify historical success, compare the eleven declared dependency coordinates in order, retain every differing coordinate in the frontier, and keep current acceptance NotEstablished",
            "counterexample": "main commit differs from the historical run commit while all eleven dependency coordinates agree; forcing replay from commit inequality alone would be overbroad",
            "replay": "timeout 30s python3 run.py",
            "residual": "an empty frontier proves only pin continuity, not current execution, environment continuity, semantic certificate acceptance, social trust, 0090 coverage, 0092 promotion, arithmetic universality or an M6 filler"
        },
        "public_scope": "Only public artifact coordinates are serialized; motivations or private narratives for earlier isolation are deliberately outside this record.",
        "claim_boundary": "Finite evidence plumbing only. Additive-zero and multiplicative-unit normalization are untouched and their histories remain separate."
    }
    before_serialization = time.perf_counter_ns()
    canonical_bytes(outcome)
    outcome["cost"]["serialization_ns"] = time.perf_counter_ns() - before_serialization
    previous = -1
    while previous != outcome["cost"]["serialized_bytes"]:
        previous = outcome["cost"]["serialized_bytes"]
        outcome["cost"]["serialized_bytes"] = len(canonical_bytes(outcome))
    data = canonical_bytes(outcome)
    (ROOT / "outcome.json").write_bytes(data)
    print(json.dumps({
        "status": outcome["status"],
        "cases": len(rows),
        "checks": checks,
        "baseline_bytes": len(baseline_bytes),
        "explicit_bytes": len(explicit_bytes),
        "serialized_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
