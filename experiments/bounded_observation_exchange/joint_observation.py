"""Two exact finite instances; constraints are external observations, not Adva cells."""
import hashlib
import json
import resource
import signal
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VISITS = 0


def timeout(signum, frame):
    raise TimeoutError("wall budget")


def inside(point, rule):
    global VISITS
    VISITS += 1
    if VISITS > 10000:
        raise TimeoutError("predicate visit budget")
    a, b, lo, hi = rule
    return lo <= a * point[0] + b * point[1] <= hi


def combine(current, constraint, complete=True):
    if not complete:
        return "UnknownCoverage", set(current)
    following = current & constraint
    if not following:
        return "Conflict", following
    return ("EvidenceStutter" if following == current else "Refined"), following


def one(spec):
    n = spec["n"]
    points = {(i, j) for i in range(n + 1) for j in range(n + 1 - i)}
    A = {p for p in points if inside(p, spec["A"])}
    B = {p for p in points if inside(p, spec["B"])}
    status, joint = combine(A, B)
    truth = tuple(spec["truth"])
    assert status == "Refined" and truth in joint
    # Independent integer inverse of s=i+j, d=i-j, retaining parity and domain.
    inverse = set()
    for s in range(spec["A"][2], spec["A"][3] + 1):
        for d in range(spec["B"][2], spec["B"][3] + 1):
            if (s + d) % 2 == 0:
                i, j = (s + d) // 2, (s - d) // 2
                if i >= 0 and j >= 0 and i + j <= n:
                    inverse.add((i, j))
    assert inverse == joint
    assert combine(A, A) == ("EvidenceStutter", A)
    assert combine(A, B, complete=False) == ("UnknownCoverage", A)
    assert combine(A, joint) == ("Refined", joint)
    assert combine(joint, B) == ("EvidenceStutter", joint)
    assert (points & A) & B == (points & B) & A
    incompatible = {p for p in points if inside(p, [1, 1, 0, 1])}
    assert combine(A, incompatible) == ("Conflict", set())
    # A fabricated narrow observation can eliminate truth despite nonempty shrinkage.
    false_constraint = {p for p in points if inside(p, [1, -1, 0, 0])}
    false_status, false_joint = combine(A, false_constraint)
    assert false_status == "Refined" and truth not in false_joint
    return {"input": spec, "counts": {"initial": len(points), "A": len(A),
            "B": len(B), "joint": len(joint), "repeat_A": len(A)},
            "A_points": sorted(A), "B_points": sorted(B), "joint_points": sorted(joint),
            "status": status, "truth_retained": True, "inverse_oracle_equal": True,
            "controls": {"repeat": "EvidenceStutter", "missing_coverage": "UnknownCoverage",
                         "conflict": "Conflict", "repeat_B_after_joint": "EvidenceStutter",
                         "order_independent_set": True,
                         "false_constraint": {"status": false_status, "truth_retained": False,
                                              "points": sorted(false_joint)}},
            "residual": "Multiple points remain; source soundness is an assumption, not established by shrinkage."}


def main():
    started = time.perf_counter()
    resource.setrlimit(resource.RLIMIT_AS, (134217728, 134217728))
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(5)
    raw = (ROOT / "round-02-contract.json").read_bytes()
    contract = json.loads(raw)
    try:
        cases = [one(spec) for spec in contract["instances"]]
        verified = time.perf_counter()
        encoded = json.dumps(cases).encode()
        restored = json.loads(encoded)
        for original, replay in zip(cases, restored):
            for field in ("A_points", "B_points", "joint_points"):
                assert [tuple(p) for p in replay[field]] == original[field]
            assert replay["counts"] == original["counts"]
        replayed = time.perf_counter()
        result = {"status": "FiniteCalibrationPassed", "cases": cases,
                  "contract_sha256": hashlib.sha256(raw).hexdigest(),
                  "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "metrics": {"construct_and_verify_seconds": verified-started,
                              "serialization_replay_seconds": replayed-verified,
                              "predicate_visits": VISITS,
                              "peak_rss_KiB_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                              "excluded": "research, coding, network, publication, final metric-file write"}}
    except (TimeoutError, MemoryError) as error:
        result = {"status": "Unknown", "reason": str(error), "predicate_visits": VISITS}
    payload = (json.dumps(result, indent=2) + "\n").encode()
    if len(payload) > 131072:
        payload = b'{"status":"Unknown","reason":"artifact byte budget"}\n'
    before_write = time.perf_counter()
    (ROOT / "joint-evidence.json").write_bytes(payload)
    write_seconds = time.perf_counter() - before_write
    cost = {"evidence_write_seconds": write_seconds, "elapsed_seconds": time.perf_counter()-started,
            "peak_rss_KiB_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (ROOT / "joint-cost.json").write_text(json.dumps(cost, indent=2) + "\n")
    signal.alarm(0)
    print(json.dumps({"status": result["status"], "counts": [x["counts"] for x in result.get("cases", [])],
                      "metrics": result.get("metrics"), "cost": cost}, indent=2))


if __name__ == "__main__":
    main()
