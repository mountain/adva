#!/usr/bin/env python3
"""Private, root-local external receipt merge; no native adva authority."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import resource
import signal
import types

SOURCE_SHA = "66824a1982bc7576c0ca53aa8f3e8ec5dde1c6db329b9ff931258d8278f06187"
LIBRARY_SHA = "29c2db4ac3e23256a81a050a2466bc566fb735c5648443b16976b9a5c756ebfb"
MAX_BYTES = 262144
PURPOSE = ("Preserve Mingli Yuan's stated direction: subject-neutral, subject-friendly "
           "cooperation helping Mingli Yuan and Jiamin Zhao; retain exact results, "
           "unresolved obligations and the private boundary.")


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def load_dependency():
    path = Path(__file__).resolve().parents[1] / "finite_split" / "calibration.py"
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES or hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError("pinned finite split checker mismatch")
    module = types.ModuleType("finite_split_pinned_dependency")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


OLD = load_dependency()


def strict_read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    def invalid_constant(_):
        raise ValueError("non-finite JSON constant")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("input file exceeds bound")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)


def save_new(path, value):
    data = encoded(value) + b"\n"
    if len(data) > MAX_BYTES:
        raise ValueError("output file exceeds bound")
    with path.open("xb") as stream:
        stream.write(data)
    return len(data)


def root_question(coefficients=(2, 3, 1), right_work=7, target_coefficients=None):
    q = OLD.question(coefficients)
    if target_coefficients is not None:
        q["target"]["coefficients"] = list(target_coefficients)
    return {"schema": "adva.private-merge-root.research", "version": 0,
            "question": q, "subject": {"role": "subject", "name": "finite-observer-v0",
                                        "identity_authority": "root-local-neutral-role"},
            "value_direction": PURPOSE, "purpose_status": "assistant-operationalization",
            "library_contract": {"path": "docs/research/0145-finite-split-contract.json",
                                 "sha256": LIBRARY_SHA},
            "privacy": {"policy": "private-only", "network_actions": False, "publication": "out-of-scope"},
            "allocation": {"root_grant": 256, "fork_cost": 1, "merge_reserve": 64,
                           "unallocated_frozen": 256 - 1 - (5 + 64) - (right_work + 64) - 64},
            "branches": {"left": {"inputs": [-3, -2, -1], "work": 5, "reserve": 64},
                         "right": {"inputs": [0, 1, 2, 3], "work": right_work, "reserve": 64}}}


def profile(root):
    return {k: copy.deepcopy(root[k]) for k in
            ("subject", "value_direction", "purpose_status", "library_contract", "privacy")}


def validate_root(root):
    OLD.validate_question(root["question"])
    work = root["branches"]["right"]["work"]
    if type(work) is not int or work not in (2, 7):
        raise ValueError("unsupported right branch allocation")
    expected = root_question(root["question"]["source"]["coefficients"], work,
                             root["question"]["target"]["coefficients"])
    if encoded(root) != encoded(expected):
        raise ValueError("root contract, policy, role or allocation mismatch")


def make_branch(root, branch_id, meter):
    """Fixture producer; the independent checker is only called by merge."""
    branch = root["branches"][branch_id]
    q = copy.deepcopy(root["question"])
    q["inputs"] = branch["inputs"].copy()
    ledger = OLD.Ledger(meter, branch["work"])
    ledger.charge("verification")
    receipt = OLD.produce(q, ledger, "normal")
    ledger.charge("serialization")
    return {"schema": "adva.private-child-receipt.research", "version": 0,
            "root_digest": sha(root), "branch_id": branch_id, "profile": profile(root),
            "question": q, "receipt": receipt, "final_ledger": ledger.snapshot()}


def merge(root, receipts, meter):
    """Audit every supplied unique receipt before selecting a mathematical verdict."""
    audit = OLD.Ledger(meter, 0, audit_only=True)
    unique, arrivals, checked, pending, counterexamples, decisions = {}, [], [], [], [], []
    root_valid = False
    evidence_valid = False
    status, reason = "Blocked", "unvalidated input"
    try:
        audit.charge("verification")
        validate_root(root)
        root_valid = True
        if type(receipts) is not list or len(receipts) > 3:
            raise ValueError("at most three child receipts")
        for wrapper in receipts:
            audit.charge("verification")
            if type(wrapper) is not dict or set(wrapper) != {
                    "schema", "version", "root_digest", "branch_id", "profile", "question", "receipt", "final_ledger"}:
                raise ValueError("child wrapper schema mismatch")
            if wrapper["schema"] != "adva.private-child-receipt.research" or type(wrapper["version"]) is not int or wrapper["version"] != 0:
                raise ValueError("child wrapper version mismatch")
            bid = wrapper["branch_id"]
            if type(bid) is not str or bid not in root["branches"]:
                raise ValueError("root-local branch id mismatch")
            if wrapper["root_digest"] != sha(root) or encoded(wrapper["profile"]) != encoded(profile(root)):
                raise ValueError("root, subject, purpose, library or privacy binding mismatch")
            q = copy.deepcopy(root["question"])
            q["inputs"] = root["branches"][bid]["inputs"].copy()
            if encoded(wrapper["question"]) != encoded(q):
                raise ValueError("branch observation scope mismatch")
            work = root["branches"][bid]["work"]
            events = wrapper["receipt"]["events"]
            if type(events) is not list or len(events) > work:
                raise ValueError("branch work exceeded grant")
            n = len(events)
            expected = {"initial": work + 64, "work_limit": work, "reserve": 64,
                        "spent": {"work": n, "verification": 1, "serialization": 1},
                        "remaining": work + 62 - n, "audit_only": False}
            execution_expected = copy.deepcopy(expected)
            execution_expected["spent"]["serialization"] = 0
            execution_expected["remaining"] += 1
            if encoded(wrapper["receipt"]["execution_ledger"]) != encoded(execution_expected):
                raise ValueError("inner execution ledger exceeds or differs from delegated grant")
            if encoded(wrapper["final_ledger"]) != encoded(expected):
                raise ValueError("copied, reset or inconsistent child grant")
            audit.charge("verification")
            receipt_digest = sha(wrapper)
            arrivals.append({"branch_id": bid, "receipt_digest": receipt_digest})
            if bid in unique:
                if encoded(unique[bid]) != encoded(wrapper):
                    raise ValueError("conflicting duplicate branch id")
            else:
                unique[bid] = wrapper
        for bid in sorted(unique):
            wrapper = unique[bid]
            decision = OLD.independently_check(wrapper["question"], wrapper["receipt"], audit)
            decisions.append({"branch_id": bid, **decision})
            if decision["decision"] != "Accepted":
                raise ValueError("independent branch checker: " + decision["reason"])
        audit.charge("verification")
        for bid, branch in root["branches"].items():
            if bid not in unique:
                pending.append({"branch_id": bid, "points": branch["inputs"], "reason": "missing receipt"})
                continue
            receipt = unique[bid]["receipt"]
            checked.extend(receipt["checked"])
            pending.extend({"branch_id": bid, "points": node["points"], "reason": receipt["status"]}
                           for node in receipt["pending"])
            if receipt["counterexample"] is not None:
                counterexamples.append({"branch_id": bid, **receipt["counterexample"]})
        atoms = checked + [x for node in pending for x in node["points"]]
        if sorted(atoms) != root["question"]["inputs"] or len(atoms) != len(set(atoms)):
            raise ValueError("merged coverage mismatch")
        evidence_valid = True
        status = "Refuted" if counterexamples else "Unknown" if pending else "FiniteMergeVerified"
        reason = {"Refuted": "checked root-scoped counterexample; unresolved atoms retained",
                  "Unknown": "missing or unfinished allocated branch obligations",
                  "FiniteMergeVerified": "all seven declared values independently checked"}[status]
    except (ValueError, TypeError, KeyError, IndexError, RecursionError, OverflowError) as error:
        status, reason = "Blocked", str(error)
    except RuntimeError as error:
        status, reason = "Unknown", str(error)
    if not evidence_valid:
        checked, counterexamples = [], []
        pending = [{"branch_id": bid, "points": xs, "reason": "original frontier retained"}
                   for bid, xs in (("left", [-3, -2, -1]), ("right", [0, 1, 2, 3]))]
    audit.charge("serialization")
    accepted_ids = sorted(unique) if evidence_valid else []
    child_spent = sum(sum(unique[bid]["final_ledger"]["spent"].values()) for bid in accepted_ids)
    historical = {"fork_cost": 1 if root_valid else None, "accepted_unique_child_spent": child_spent,
                  "known_spent": 1 + child_spent if root_valid else None,
                  "accepted_branch_ids": accepted_ids,
                  "missing_branch_grants_stay_reserved": True, "refunds": 0,
                  "reserved_unreported": {bid: branch["work"] + branch["reserve"]
                                          for bid, branch in root["branches"].items() if bid not in accepted_ids} if root_valid else None,
                  "accepted_unused_stays_reserved": {bid: unique[bid]["final_ledger"]["remaining"] for bid in accepted_ids}}
    semantic = {"status": status, "root_digest": sha(root), "checked": sorted(checked),
                "pending": pending, "counterexamples": counterexamples,
                "capability": "external-merge-checkpoint" if status == "FiniteMergeVerified" else None,
                "native_free": "Unimplemented", "human_satisfaction": "Unverified"}
    return {"schema": "adva.private-merge-report.research", "version": 0,
            "semantic": semantic, "reason": reason, "arrival_history": arrivals,
            "branch_checks": decisions, "historical_resource": historical,
            "current_audit_resource": audit.snapshot(), "global_physical_spent": meter.spent,
            "allocation": copy.deepcopy(root.get("allocation")) if type(root) is dict else None,
            "branch_allocations": copy.deepcopy(root.get("branches")) if type(root) is dict else None,
            "audit_semantics": "read-only audit of immutable input snapshot; separately declared current 64-unit audit allowance, not a reset or second funded native action",
            "ledger_model": "single-invocation external model; no globally committed ledger or refunds",
            "retained_submitted_material": receipts if not evidence_valid else None,
            "root_profile": profile(root) if root_valid else None,
            "purpose_status": "assistant-operationalization", "publication": "not granted; out-of-scope"}


def restrict_runtime():
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024**2, 256 * 1024**2))
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    signal.alarm(5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    restrict_runtime()
    meter = OLD.Meter()
    try:
        root, receipts = strict_read(args.root), strict_read(args.receipts)
        report = merge(root, receipts, meter)
    except (ValueError, TypeError, KeyError, IndexError, UnicodeError, RecursionError) as error:
        report = {"schema": "adva.private-merge-report.research", "version": 0,
                  "semantic": {"status": "Blocked", "native_free": "Unimplemented", "capability": None},
                  "reason": "input parse/shape: " + str(error), "global_physical_spent": meter.spent,
                  "retained_input_paths": [str(args.root), str(args.receipts)]}
    size = save_new(args.output, report)
    print(json.dumps({"status": report["semantic"]["status"], "physical_units": meter.spent, "report_bytes": size}))


if __name__ == "__main__":
    main()
