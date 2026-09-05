"""External finite calibration: coverage is required before feature closure.

No native Adva identity, certificate, word promotion, or halting oracle.
The positive/negative roles are assumptions of a finite toy truth table.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import resource
import signal
import time
from fractions import Fraction


SCHEMA = "adva.external.prefix-coverage-gate.v0"
CONTRACT = {
    "scope": "full binary leaves at declared depth; P/N assumed, A/M free",
    "depths_exhausted": [2],
    "observers_exhausted": [1, 2],
    "roles": ["P", "N", "A", "M"],
    "observer": "floor(2**k * positive_mass), including mass=1",
    "max_nodes": 10000,
    "max_seconds": 30,
    "max_address_space_bytes": 268435456,
    "max_output_bytes": 1048576,
    "routes": 1,
    "automatic_continuations": 0,
}


class Exhausted(Exception):
    pass


class Budget:
    def __init__(self, nodes=10000, seconds=30):
        self.remaining = nodes
        self.used = 0
        self.deadline = time.monotonic() + seconds

    def tick(self):
        if self.remaining <= 0 or time.monotonic() >= self.deadline:
            raise Exhausted("Unknown: finite run budget exhausted")
        self.remaining -= 1
        self.used += 1


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n"


def state(depth, positive, negative, unresolved, history=()):
    return {"depth": depth, "P": list(positive), "N": list(negative),
            "A": list(unresolved), "history": list(history)}


def validate(s):
    d = s["depth"]
    if type(d) is not int or not 1 <= d <= 8:
        raise ValueError("depth outside finite reference carrier [1,8]")
    prefixes = []
    for role in ("P", "N", "A"):
        if type(s[role]) is not list or len(s[role]) > 256:
            raise ValueError("invalid or oversized prefix list")
        for q in s[role]:
            if type(q) is not str or len(q) > d or any(c not in "01" for c in q):
                raise ValueError("invalid binary prefix")
            prefixes.append(q)
    if len(prefixes) > 256:
        raise ValueError("oversized combined prefix list")
    for i, q in enumerate(prefixes):
        for r in prefixes[i + 1:]:
            if q.startswith(r) or r.startswith(q):
                raise ValueError("duplicate, overlap, or non-antichain status regions")


def leaves(s):
    validate(s)
    return tuple(format(i, f"0{s['depth']}b") for i in range(1 << s["depth"]))


def region(s, role):
    return tuple(x for x in leaves(s) if any(x.startswith(q) for q in s[role]))


def mass(prefixes):
    return sum((Fraction(1, 1 << len(q)) for q in prefixes), Fraction())


def ratio(q):
    return [q.numerator, q.denominator]


def cell(q, k):
    if type(k) is not int or not 1 <= k <= 8:
        raise ValueError("observer precision outside [1,8]")
    return (q.numerator * (1 << k)) // q.denominator


def interval_only(s, k):
    """Deliberately unsafe negative control: silently ignores missing leaves."""
    validate(s)
    lo = mass(s["P"])
    hi = lo + mass(s["A"])
    return {"verdict": "FeatureClosed" if cell(lo, k) == cell(hi, k) else "Open",
            "L": ratio(lo), "U": ratio(hi)}


def coverage_gate(s, k):
    universe = leaves(s)
    covered = set(region(s, "P")) | set(region(s, "N")) | set(region(s, "A"))
    missing = [x for x in universe if x not in covered]
    lo = mass(s["P"])
    record = {"input": s, "observer_bits": k, "L": ratio(lo),
              "coverage_missing": missing, "residual": list(s["A"]),
              "history": list(s["history"])}
    cell(lo, k)  # Validate the observer even when coverage is absent.
    if missing:
        return dict(record, verdict="CertificateObstruction", U=None,
                    reason="Uncovered legal leaves remain possible-positive")
    hi = lo + mass(s["A"])
    closed = cell(lo, k) == cell(hi, k)
    return dict(record, verdict="FeatureClosed" if closed else "Open",
                U=ratio(hi), feature=cell(lo, k) if closed else None,
                object_closed=not s["A"])


def oracle(s, k, budget):
    """Independent leaf-subset enumeration; does not use interval arithmetic."""
    universe = leaves(s)
    positive = set(region(s, "P"))
    negative = set(region(s, "N"))
    free = [x for x in universe if x not in positive | negative]
    witnesses = {}
    for bits in itertools.product((0, 1), repeat=len(free)):
        budget.tick()
        added = [q for q, bit in zip(free, bits) if bit]
        count = len(positive) + len(added)
        value = (count * (1 << k)) // len(universe)
        witnesses.setdefault(value, sorted(positive | set(added)))
    return {"values": sorted(witnesses), "extreme_witnesses": [
        {"feature": v, "positive_leaves": witnesses[v]}
        for v in sorted({min(witnesses), max(witnesses)})]}


def fixtures():
    return {
        "missing_eighth": state(3, ["00"], ["1"], ["010"], ["omit:011"]),
        "restored_eighth": state(3, ["00"], ["1"], ["010", "011"],
                                 ["omit:011", "restore:011"]),
        "feature_not_object": state(4, ["00", "0100"], ["1", "011"],
                                     ["0101"], ["declare:depth4"]),
        "fresh_reuse": state(4, ["000"], ["01", "1", "0011"], ["0010"],
                              ["declare:fresh-depth4"]),
    }


def build_witness(budget=None):
    budget = budget or Budget()
    rows = []
    false_closes = 0
    blocked = 0
    for assignment in itertools.product(CONTRACT["roles"], repeat=4):
        budget.tick()
        words = [format(i, "02b") for i in range(4)]
        s = state(2, *([q for q, r in zip(words, assignment) if r == role]
                       for role in ("P", "N", "A")))
        for k in CONTRACT["observers_exhausted"]:
            safe = coverage_gate(s, k)
            bad = interval_only(s, k)
            truth = oracle(s, k, budget)
            if safe["verdict"] == "FeatureClosed":
                assert truth["values"] == [safe["feature"]]
            if safe["verdict"] == "Open":
                assert len(truth["values"]) > 1
            false_closes += bad["verdict"] == "FeatureClosed" and len(truth["values"]) > 1
            blocked += safe["verdict"] == "CertificateObstruction"
            rows.append({"assignment": "".join(assignment), "k": k,
                         "unsafe": bad["verdict"], "safe": safe["verdict"],
                         "missing": safe["coverage_missing"], "oracle": truth["values"]})
    cases = {}
    for name, s in fixtures().items():
        budget.tick()
        k = 2
        finer = 4 if name == "fresh_reuse" else 3
        cases[name] = {"safe": coverage_gate(s, k), "unsafe": interval_only(s, k),
                       "oracle": oracle(s, k, budget),
                       "finer": coverage_gate(s, finer),
                       "finer_oracle": oracle(s, finer, budget)}
    assert cases["missing_eighth"]["safe"]["verdict"] == "CertificateObstruction"
    assert cases["missing_eighth"]["unsafe"]["verdict"] == "FeatureClosed"
    assert cases["restored_eighth"]["safe"]["verdict"] == "Open"
    for name in ("feature_not_object", "fresh_reuse"):
        assert cases[name]["safe"]["verdict"] == "FeatureClosed"
        assert not cases[name]["safe"]["object_closed"]
        assert cases[name]["finer"]["verdict"] == "Open"
    return {"schema": SCHEMA, "contract": CONTRACT, "rows": rows, "cases": cases,
            "counts": {"states": 256, "observer_checks": len(rows),
                       "unsafe_false_closes": false_closes, "coverage_obstructions": blocked,
                       "enumerated_nodes": budget.used},
            "word": {"name": "coverage-gated-close", "status": "Proposed",
                     "meaning": "Require explicit full-scope coverage before scalar feature closure",
                     "native_word": False, "new_theorem": False}}


def verify_witness(obj):
    # Whole-contract replay rejects changed inputs, schemas, outcomes, or omitted rows.
    return canonical(obj) == canonical(build_witness())


def enforce_limits():
    resource.setrlimit(resource.RLIMIT_AS, (268435456, 268435456))
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))

    def timeout(_signum, _frame):
        raise Exhausted("Unknown: wall-clock limit")

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check")
    args = parser.parse_args()
    enforce_limits()
    if args.check:
        with open(args.check, encoding="utf-8") as f:
            obj = json.load(f)
        if not verify_witness(obj):
            raise SystemExit("replay mismatch")
        print("Exact witness replay passed")
        return
    start = time.perf_counter_ns()
    witness = build_witness()
    built = time.perf_counter_ns()
    encoded = canonical(witness)
    serialized = time.perf_counter_ns()
    assert len(encoded.encode()) <= CONTRACT["max_output_bytes"]
    assert verify_witness(json.loads(encoded))
    verified = time.perf_counter_ns()
    fresh = fixtures()["fresh_reuse"]
    assert coverage_gate(fresh, 2)["verdict"] == "FeatureClosed"
    reused = time.perf_counter_ns()
    metrics = {"construction_and_enumeration_ns": built - start,
               "serialization_ns": serialized - built,
               "parse_and_full_replay_ns": verified - serialized,
               "fresh_input_construction_and_reuse_ns": reused - verified,
               "measured_phase_total_ns": reused - start,
               "process_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               "artifact_bytes_not_memory": len(encoded.encode()),
               "sha256": hashlib.sha256(encoded.encode()).hexdigest(),
               "total_enumerated_nodes_build_and_replay": 2 * witness["counts"]["enumerated_nodes"],
               "unmeasured": ["research design and source authoring", "imports", "OS scheduling",
                              "test-suite child process", "network and repository persistence",
                              "physical energy", "customer use value"],
               "timing_is_not_a_ci_gate": True}
    print(canonical({"witness": witness, "metrics": metrics}), end="")


if __name__ == "__main__":
    main()
