#!/usr/bin/env python3
"""Finite receiver calibration for implementation failure vs counterexample."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


WORK = 0


def count(n: int = 1) -> None:
    global WORK
    WORK += n
    if WORK > 100_000:
        raise RuntimeError("host-work budget exceeded")


def canonical(value: Any) -> str:
    count()
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    count()
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def words(width: int) -> list[str]:
    count(2**width)
    return ["".join(bits) for bits in itertools.product("01", repeat=width)]


def snapshot(family: dict[str, Any]) -> dict[str, Any]:
    width = family["width"]
    stage = family["early_stage"]
    machine = family["machine"]
    universe = words(width)
    history = [
        {"program": program, "stage": reveal}
        for program, reveal in sorted(machine.items(), key=lambda item: (item[1], item[0]))
        if reveal <= stage
    ]
    unresolved = [program for program in universe if program not in {x["program"] for x in history}]
    core = {
        "family": family["name"],
        "width": width,
        "early_stage": stage,
        "machine": machine,
        "proposal": family["proposal"],
    }
    count(len(universe) + len(history))
    return {
        "object": core,
        "object_digest": digest(core),
        "history": history,
        "history_digest": digest(history),
        "unresolved": unresolved,
        "unresolved_digest": digest(unresolved),
    }


def preservation(snapshot_: dict[str, Any]) -> dict[str, Any]:
    return {
        key: snapshot_[key]
        for key in (
            "object_digest",
            "history",
            "history_digest",
            "unresolved",
            "unresolved_digest",
        )
    }


def valid_failure(receipt: dict[str, Any]) -> bool:
    count(5)
    return (
        receipt.get("kind") == "implementation-failure"
        and receipt.get("phase") in {"load", "execute", "serialize"}
        and receipt.get("code") in {"InterfaceUnavailable", "BudgetExceeded", "InternalError"}
        and receipt.get("semantic_conclusion") is None
        and receipt.get("candidate") is None
    )


def receive(snapshot_: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    count(4)
    if receipt.get("object_digest") != snapshot_["object_digest"]:
        return {"outcome": "InvalidEvidence", "reason": "ObjectBindingMismatch"}
    if receipt.get("history_digest") != snapshot_["history_digest"]:
        return {"outcome": "InvalidEvidence", "reason": "HistoryBindingMismatch"}
    if receipt.get("unresolved_digest") != snapshot_["unresolved_digest"]:
        return {"outcome": "InvalidEvidence", "reason": "UnresolvedBindingMismatch"}

    if receipt.get("kind") == "implementation-failure":
        if not valid_failure(receipt):
            return {"outcome": "InvalidEvidence", "reason": "MalformedImplementationFailure"}
        return {
            "outcome": "ImplementationFailure",
            "reason": receipt["code"],
            "preserved": preservation(snapshot_),
            "semantic_delta": {"accepted": [], "rejected": []},
        }

    if receipt.get("kind") != "semantic-candidate":
        return {"outcome": "InvalidEvidence", "reason": "UnknownReceiptKind"}

    candidate = receipt.get("candidate")
    if not isinstance(candidate, dict) or set(candidate) != {"program", "stage"}:
        return {"outcome": "InvalidEvidence", "reason": "MalformedCandidate"}
    program = candidate["program"]
    stage = candidate["stage"]
    obj = snapshot_["object"]
    count(6)
    if type(program) is not str or len(program) != obj["width"] or set(program) - {"0", "1"}:
        return {"outcome": "InvalidEvidence", "reason": "CandidateOutsideSyntax"}
    if type(stage) is not int or stage < 0:
        return {"outcome": "InvalidEvidence", "reason": "InvalidCandidateStage"}
    if obj["machine"].get(program) != stage:
        return {"outcome": "InvalidEvidence", "reason": "EventNotInBoundMachine"}
    if stage <= obj["early_stage"]:
        return {"outcome": "InvalidEvidence", "reason": "NotDelayed"}
    if program in obj["proposal"]:
        return {"outcome": "InvalidEvidence", "reason": "DoesNotRefuteProposal"}
    if program not in snapshot_["unresolved"]:
        return {"outcome": "InvalidEvidence", "reason": "NotInPreservedResidual"}
    return {
        "outcome": "Counterexample",
        "witness": candidate,
        "refutes": {"claimed_complete_domain": obj["proposal"]},
        "preserved": preservation(snapshot_),
        "semantic_delta": {"accepted": [program], "rejected": []},
    }


def bound_receipt(snapshot_: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    count(3)
    return {
        **body,
        "object_digest": snapshot_["object_digest"],
        "history_digest": snapshot_["history_digest"],
        "unresolved_digest": snapshot_["unresolved_digest"],
    }


def run_family(family: dict[str, Any]) -> dict[str, Any]:
    snap = snapshot(family)
    expected_preservation = preservation(snap)
    failure_results = []
    for phase, code in (
        ("load", "InterfaceUnavailable"),
        ("execute", "BudgetExceeded"),
        ("serialize", "InternalError"),
    ):
        receipt = bound_receipt(
            snap,
            {
                "kind": "implementation-failure",
                "phase": phase,
                "code": code,
                "semantic_conclusion": None,
                "candidate": None,
            },
        )
        result = receive(snap, receipt)
        assert result["outcome"] == "ImplementationFailure"
        assert result["preserved"] == expected_preservation
        assert result["semantic_delta"] == {"accepted": [], "rejected": []}
        failure_results.append(result)

    witness_receipt = bound_receipt(
        snap,
        {"kind": "semantic-candidate", "candidate": family["delayed_witness"]},
    )
    counterexample = receive(snap, witness_receipt)
    assert counterexample["outcome"] == "Counterexample"
    assert counterexample["preserved"] == expected_preservation

    # A repaired checker resumes from precisely the snapshot retained by every failure.
    for failed in failure_results:
        assert failed["preserved"] == counterexample["preserved"]

    controls: list[tuple[str, dict[str, Any], str]] = []
    controls.append((
        "failure_relabelled_counterexample",
        bound_receipt(snap, {"kind": "semantic-candidate", "candidate": None}),
        "MalformedCandidate",
    ))
    controls.append((
        "failure_with_semantic_conclusion",
        bound_receipt(snap, {"kind": "implementation-failure", "phase": "execute", "code": "InternalError", "semantic_conclusion": "false", "candidate": None}),
        "MalformedImplementationFailure",
    ))
    controls.append((
        "failure_with_candidate",
        bound_receipt(snap, {"kind": "implementation-failure", "phase": "execute", "code": "InternalError", "semantic_conclusion": None, "candidate": family["delayed_witness"]}),
        "MalformedImplementationFailure",
    ))
    fabricated = dict(family["delayed_witness"])
    fabricated["stage"] += 1
    controls.append((
        "fabricated_event",
        bound_receipt(snap, {"kind": "semantic-candidate", "candidate": fabricated}),
        "EventNotInBoundMachine",
    ))
    already_visible = snap["history"][0]
    controls.append((
        "already_visible_event",
        bound_receipt(snap, {"kind": "semantic-candidate", "candidate": already_visible}),
        "NotDelayed",
    ))
    bad_object = bound_receipt(snap, {"kind": "semantic-candidate", "candidate": family["delayed_witness"]})
    bad_object["object_digest"] = "0" * 64
    controls.append(("changed_object", bad_object, "ObjectBindingMismatch"))
    bad_history = bound_receipt(snap, {"kind": "implementation-failure", "phase": "load", "code": "InterfaceUnavailable", "semantic_conclusion": None, "candidate": None})
    bad_history["history_digest"] = "1" * 64
    controls.append(("changed_history", bad_history, "HistoryBindingMismatch"))
    bad_unresolved = bound_receipt(snap, {"kind": "implementation-failure", "phase": "load", "code": "InterfaceUnavailable", "semantic_conclusion": None, "candidate": None})
    bad_unresolved["unresolved_digest"] = "2" * 64
    controls.append(("changed_unresolved", bad_unresolved, "UnresolvedBindingMismatch"))
    controls.append((
        "boolean_stage",
        bound_receipt(snap, {"kind": "semantic-candidate", "candidate": {"program": family["delayed_witness"]["program"], "stage": True}}),
        "InvalidCandidateStage",
    ))
    controls.append((
        "unknown_failure_code",
        bound_receipt(snap, {"kind": "implementation-failure", "phase": "execute", "code": "Counterexample", "semantic_conclusion": None, "candidate": None}),
        "MalformedImplementationFailure",
    ))

    control_results = []
    for name, receipt, reason in controls:
        result = receive(snap, receipt)
        assert result == {"outcome": "InvalidEvidence", "reason": reason}, (name, result)
        control_results.append({"name": name, **result})

    return {
        "family": family["name"],
        "snapshot": snap,
        "implementation_failures": failure_results,
        "counterexample": counterexample,
        "controls": control_results,
        "assertions": 3 * 3 + 2 + 3 + len(controls),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    assert contract["schema"] == "adva.external.failure-kind-boundary.contract.v0"
    families = [run_family(family) for family in contract["families"]]
    evidence = {
        "schema": "adva.external.failure-kind-boundary.evidence.v0",
        "base": contract["base"],
        "status": "Passed",
        "result": "ImplementationFailureSeparatedFromCounterexample",
        "new_vocabulary": [],
        "families": families,
        "family_count": len(families),
        "implementation_failure_cases": sum(len(x["implementation_failures"]) for x in families),
        "semantic_counterexamples": sum(x["counterexample"]["outcome"] == "Counterexample" for x in families),
        "negative_controls": sum(len(x["controls"]) for x in families),
        "assertions": sum(x["assertions"] for x in families),
        "host_work_units": WORK,
        "residual": "This finite receiver does not prove that arbitrary implementation failures are detectable or that unrestricted languages have decidable semantic counterexamples.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
