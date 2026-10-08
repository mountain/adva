#!/usr/bin/env python3
"""Exhaust one fixed identity-rich fork carrier and its observer quotients."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import resource
import signal
import time


HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "contract.json"
EVENTS = ("e0", "eL", "eR")
ORDER = (("e0", "eL"), ("e0", "eR"))
IDEALS = ((), ("e0",), ("e0", "eL"), ("e0", "eR"), EVENTS)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(condition: bool, label: str) -> None:
    if not condition:
        raise RuntimeError(label)


def write_new(path: Path, value: object) -> int:
    raw = canonical(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)
    return len(raw)


def valid_carrier(carrier: dict[str, object]) -> tuple[bool, str]:
    sources = carrier.get("sources")
    occurrences = carrier.get("occurrences")
    history = carrier.get("history")
    if not isinstance(sources, dict) or set(sources) != set(EVENTS):
        return False, "SourceCoverage"
    if not isinstance(occurrences, dict) or set(occurrences) != set(EVENTS):
        return False, "OccurrenceCoverage"
    if len(set(occurrences.values())) != len(EVENTS):
        return False, "OccurrenceIdentityCollision"
    if not isinstance(history, list) or sorted(history) != sorted(EVENTS):
        return False, "HistoryCoverage"
    position = {event: index for index, event in enumerate(history)}
    if any(position[lower] >= position[upper] for lower, upper in ORDER):
        return False, "HistoryPrecedence"
    return True, "ValidCarrier"


def valid_ideal(ideal: tuple[str, ...]) -> tuple[bool, str]:
    if any(event not in EVENTS for event in ideal):
        return False, "UnknownEvent"
    selected = set(ideal)
    if any(upper in selected and lower not in selected for lower, upper in ORDER):
        return False, "NotDownwardClosed"
    return True, "ValidIdeal"


def event_observation(ideal: tuple[str, ...]) -> tuple[int, ...]:
    selected = set(ideal)
    return tuple(int(event in selected) for event in EVENTS)


def exact_observation(state: dict[str, object], fields: tuple[str, ...]) -> tuple[object, ...]:
    carrier = state["carrier"]
    result: list[object] = [event_observation(state["ideal"])]
    if "source" in fields:
        result.append(tuple(carrier["sources"][event] for event in EVENTS))
    if "occurrence" in fields:
        result.append(tuple(carrier["occurrences"][event] for event in EVENTS))
    if "history" in fields:
        result.append(tuple(carrier["history"]))
    return tuple(result)


def collision_count(states: list[dict[str, object]], fields: tuple[str, ...]) -> int:
    count = 0
    for left, right in itertools.combinations(states, 2):
        if exact_observation(left, fields) == exact_observation(right, fields):
            count += 1
    return count


def main(output: Path) -> int:
    started = time.monotonic()
    if output.exists():
        raise SystemExit("ExistingOutput")
    contract = json.loads(CONTRACT.read_bytes())
    require(contract["status"] == "FrozenBeforeExecution", "ContractStatus")
    require(sha256(Path(__file__).read_bytes()) == contract["pins"]["source_sha256"],
            "SourcePin")
    signal.signal(signal.SIGALRM,
                  lambda *_: (_ for _ in ()).throw(TimeoutError("WallLimit")))
    signal.setitimer(signal.ITIMER_REAL, contract["limits"]["wall_seconds"])
    checks = 2
    comparisons = 0
    serialized_bytes = 0
    try:
        carriers: list[dict[str, object]] = []
        for source_swap, occurrence_swap, history_swap in itertools.product((0, 1), repeat=3):
            sources = {"e0": "s0", "eL": "sR" if source_swap else "sL",
                       "eR": "sL" if source_swap else "sR"}
            occurrences = {"e0": "o0", "eL": "oR" if occurrence_swap else "oL",
                           "eR": "oL" if occurrence_swap else "oR"}
            history = ["e0", "eR", "eL"] if history_swap else ["e0", "eL", "eR"]
            carrier = {
                "carrier_id": f"s{source_swap}-o{occurrence_swap}-h{history_swap}",
                "events": list(EVENTS), "order": [list(edge) for edge in ORDER],
                "sources": sources, "occurrences": occurrences, "history": history,
            }
            valid, reason = valid_carrier(carrier)
            require(valid and reason == "ValidCarrier", "GeneratedCarrier")
            checks += 1
            carriers.append(carrier)

        states: list[dict[str, object]] = []
        for carrier in carriers:
            for ideal in IDEALS:
                valid, reason = valid_ideal(ideal)
                require(valid and reason == "ValidIdeal", "GeneratedIdeal")
                checks += 1
                states.append({"carrier": carrier, "ideal": ideal})

        require(len(carriers) == 8 and len(states) == 40, "FrozenFamilySize")
        checks += 1
        unordered_pairs = len(states) * (len(states) - 1) // 2
        require(unordered_pairs == 780, "FrozenPairCount")
        checks += 1

        # Within one fixed exact carrier, all event-membership vectors are distinct.
        within_carrier_pairs = 0
        within_carrier_membership_collisions = 0
        count_only_collisions = 0
        membership_collisions = 0
        source_only_pairs = occurrence_only_pairs = history_only_pairs = 0
        first_witness: dict[str, object] | None = None
        for left, right in itertools.combinations(states, 2):
            comparisons += 1
            same_carrier = left["carrier"]["carrier_id"] == right["carrier"]["carrier_id"]
            same_membership = event_observation(left["ideal"]) == event_observation(right["ideal"])
            if same_carrier:
                within_carrier_pairs += 1
                if same_membership:
                    within_carrier_membership_collisions += 1
                if len(left["ideal"]) == len(right["ideal"]):
                    count_only_collisions += 1
            if same_membership and not same_carrier:
                membership_collisions += 1
                lc, rc = left["carrier"], right["carrier"]
                differences = tuple(
                    field for field in ("sources", "occurrences", "history")
                    if lc[field] != rc[field]
                )
                if differences == ("sources",):
                    source_only_pairs += 1
                elif differences == ("occurrences",):
                    occurrence_only_pairs += 1
                elif differences == ("history",):
                    history_only_pairs += 1
                if first_witness is None and differences == ("history",):
                    first_witness = {
                        "left_carrier": lc, "right_carrier": rc,
                        "common_ideal": list(left["ideal"]),
                        "common_event_observation": list(event_observation(left["ideal"])),
                        "exact_difference": ["history"],
                    }

        require(comparisons == 780, "AllPairsCompared")
        require(comparisons <= contract["limits"]["comparison_units"], "ComparisonBudget")
        require(within_carrier_pairs == 80, "WithinCarrierPairs")
        require(within_carrier_membership_collisions == 0, "MembershipSeparatesFixedCarrierIdeals")
        require(count_only_collisions == 8, "CountOnlyCollisionCount")
        require(membership_collisions == 140, "CrossCarrierMembershipCollisions")
        require((source_only_pairs, occurrence_only_pairs, history_only_pairs) == (20, 20, 20),
                "SingleFieldCollisionCounts")
        require(first_witness is not None, "HistoryCollisionWitness")
        checks += 8

        profiles = {
            "event-only": (),
            "event-source": ("source",),
            "event-source-occurrence": ("source", "occurrence"),
            "event-source-occurrence-history": ("source", "occurrence", "history"),
        }
        profile_collisions = {}
        for name, fields in profiles.items():
            value = collision_count(states, fields)
            comparisons += unordered_pairs
            profile_collisions[name] = value
        require(profile_collisions == {
            "event-only": 140,
            "event-source": 60,
            "event-source-occurrence": 20,
            "event-source-occurrence-history": 0,
        }, "RefinementCollisionCounts")
        require(comparisons <= contract["limits"]["comparison_units"], "TotalComparisonBudget")
        checks += 2

        invalid_controls = {
            "missing-source": valid_carrier({
                **carriers[0], "sources": {"e0": "s0", "eL": "sL"}}),
            "duplicate-occurrence": valid_carrier({
                **carriers[0], "occurrences": {"e0": "o0", "eL": "oL", "eR": "oL"}}),
            "precedence-violating-history": valid_carrier({
                **carriers[0], "history": ["eL", "e0", "eR"]}),
            "unknown-event": valid_ideal(("e0", "eX")),
            "omitted-prerequisite": valid_ideal(("eL",)),
        }
        require(all(not accepted for accepted, _ in invalid_controls.values()),
                "InvalidControlsRejected")
        checks += 1

        deterministic = {
            "profile": "adva.research.observer-identity-collision.v0",
            "status": "PassedFiniteCounterexample",
            "scope": {
                "events": list(EVENTS), "order": [list(edge) for edge in ORDER],
                "exact_carriers": len(carriers), "ideals_per_carrier": len(IDEALS),
                "exact_states": len(states), "unordered_state_pairs": unordered_pairs,
            },
            "result": {
                "fixed_carrier_membership_collisions": within_carrier_membership_collisions,
                "cross_carrier_membership_collisions": membership_collisions,
                "single_field_collision_pairs": {
                    "source": source_only_pairs, "occurrence": occurrence_only_pairs,
                    "history": history_only_pairs,
                },
                "profile_collision_counts": profile_collisions,
                "event_membership_is_injective_on_fixed_carrier_ideals": True,
                "event_membership_is_injective_on_identity_rich_states": False,
            },
            "witness": first_witness,
            "invalid_controls": {
                name: {"outcome": "InvalidCarrier", "reason": reason}
                for name, (accepted, reason) in invalid_controls.items()
            },
            "boundary": {
                "native_adva_carrier": False,
                "rust_certificate": False,
                "membership_probe_implementability": False,
                "abstract_counterexample_only": True,
                "does_not_refute_fixed_carrier_downset_separation": True,
                "does_refute_unqualified_lift_to_identity_rich_states": True,
                "new_vocabulary": [],
            },
        }
        output.mkdir(parents=True)
        serialized_bytes += write_new(output / "result.json", deterministic)
        for name, value in deterministic["invalid_controls"].items():
            serialized_bytes += write_new(output / "controls" / f"{name}.json", value)

        usage = resource.getrusage(resource.RUSAGE_SELF)
        execution = {
            "profile": "adva.research.observer-identity-collision.execution.v0",
            "status": "Passed",
            "assertion_checks": checks,
            "comparison_units": comparisons,
            "search_candidates": 0,
            "implementation_correction_replays": 1,
            "whole_run_seconds": time.monotonic() - started,
            "max_supervisor_rss_kib": usage.ru_maxrss,
            "serialized_bytes_before_execution": serialized_bytes,
            "source_sha256": sha256(Path(__file__).read_bytes()),
            "contract_sha256": sha256(CONTRACT.read_bytes()),
            "result_sha256": sha256(canonical(deterministic)),
        }
        write_new(output / "execution.json", execution)
        print(canonical(execution).decode("ascii"))
        return 0
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output.resolve()))
