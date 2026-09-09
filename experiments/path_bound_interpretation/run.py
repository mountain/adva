"""Finite phrase/path/matrix calibration. Standard library; no native admission."""

from __future__ import annotations

import hashlib
import json
import resource
import sys
import time
from fractions import Fraction as Q
from pathlib import Path


I = ((1, 0), (0, 1))
A = ((1, 2), (0, 1))
BASES = (I, ((0, -1), (1, 0)), ((1, 1), (0, 1)))
PHRASES = {"绕零孔 正行 1 周": 1, "绕零孔 逆行 1 周": -1,
           "绕零孔 正行 2 周": 2, "绕零孔 逆行 2 周": -2}


class Refusal(Exception):
    pass


def mm(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def mv(a, v):
    return tuple(sum(a[i][j] * v[j] for j in range(2)) for i in range(2))


def inverse(b):
    if b is None:
        raise Refusal("UnknownBasis")
    if len(b) != 2 or any(len(row) != 2 for row in b):
        raise Refusal("InvalidBasis")
    if any(type(v) is not int or abs(v).bit_length() > 64 for row in b for v in row):
        raise Refusal("InvalidBasis")
    a, c = b[0]
    d, e = b[1]
    if a * e - c * d != 1:
        raise Refusal("InvalidBasis")
    return ((e, -c), (-d, a))


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def winding(path, base):
    if not 2 <= len(path) <= 32:
        raise Refusal("UnknownVertexBudget")
    if path[0] != base:
        raise Refusal("WrongBasepoint")
    if path[-1] != base:
        raise Refusal("OpenPath")
    for point in path:
        if len(point) != 2 or any(type(v) is not Q for v in point):
            raise Refusal("InvalidCoordinate")
        if any(max(abs(v.numerator).bit_length(), v.denominator.bit_length()) > 64
               for v in point):
            raise Refusal("UnknownCoordinateBudget")
        norm = sum(v * v for v in point)
        if norm == 0:
            raise Refusal("OriginVertex")
        if norm >= Q(1, 4):
            raise Refusal("OutsideLocalDisk")
    total = 0
    for a, b in zip(path, path[1:]):
        det = cross(a, b)
        # A collinear segment contains zero exactly when its endpoints oppose.
        if det == 0 and sum(a[i] * b[i] for i in range(2)) <= 0:
            raise Refusal("OriginOnEdge")
        # Half-open crossing convention counts a ray vertex exactly once.
        if a[1] <= 0 < b[1] and det > 0:
            total += 1
        elif b[1] <= 0 < a[1] and det < 0:
            total -= 1
    return total


def point_wire(path):
    return [[str(x), str(y)] for x, y in path]


def check(phrase, path, base, basis, claimed=None):
    if phrase not in PHRASES:
        raise Refusal("UnsupportedPhrase")
    inv = inverse(basis)
    observed = winding(path, base)
    if observed != PHRASES[phrase]:
        raise Refusal("DirectionOrTurnMismatch")
    standard = ((1, 2 * observed), (0, 1))
    action = mm(mm(inv, standard), basis)
    if any(abs(v).bit_length() > 64 for row in action for v in row):
        raise Refusal("UnknownMatrixBudget")
    if claimed is not None and claimed != action:
        raise Refusal("ActionMismatch")
    q_standard = (0, 1)
    before = mv(inv, q_standard)
    after = mv(action, before)
    if mv(basis, after) != mv(standard, q_standard):
        raise AssertionError("basis transport failed")
    return {"status": "MatchedFiniteScope", "phrase": phrase,
            "basepoint": [str(v) for v in base], "path": point_wire(path),
            "basis_columns_in_reference_basis": basis,
            "observed_winding": observed, "action": action,
            "charge_before": before, "charge_after": after,
            "endpoint_closed": True, "action_identity": action == I,
            "history": {"retained_path": point_wire(path), "retained_phrase": phrase},
            "monodromy_status": "imported Research0043 convention",
            "native_admission": "not-granted"}


def diamond(radius, turns):
    zero = Q(0)
    path = ((radius, zero), (zero, radius), (-radius, zero),
            (zero, -radius), (radius, zero))
    if turns < 0:
        path = path[::-1]
    return path + path[1:] * (abs(turns) - 1)


def main():
    start = time.perf_counter()
    root = Path(__file__).resolve().parent
    raw_contract = (root / "contract.json").read_bytes()
    contract = json.loads(raw_contract)
    calls = 0

    def bounded(*args, **kwargs):
        nonlocal calls
        calls += 1
        if (calls > contract["budget"]["total_validation_calls_including_replay"]
                or time.perf_counter() - start > 30):
            raise Refusal("UnknownRunBudget")
        return check(*args, **kwargs)

    construct_start = time.perf_counter()
    inputs = [(phrase, diamond(radius, turns), (radius, Q(0)), basis)
              for phrase, turns in PHRASES.items()
              for radius in (Q(1, 8), Q(1, 16), Q(1, 32)) for basis in BASES]
    construction = time.perf_counter() - construct_start
    verify_start = time.perf_counter()
    records = [bounded(*args) for args in inputs]
    verification = time.perf_counter() - verify_start
    reuse_start = time.perf_counter()
    fresh = ((Q(1, 10), Q(0)), (Q(1, 10), Q(1, 7)), (Q(-1, 8), Q(1, 7)),
             (Q(-1, 8), Q(-1, 9)), (Q(1, 10), Q(-1, 9)), (Q(1, 10), Q(0)))
    fresh_basis = ((1, 2), (1, 3))
    records.append(bounded("绕零孔 正行 1 周", fresh, fresh[0], fresh_basis))
    reuse = time.perf_counter() - reuse_start
    control_start = time.perf_counter()
    path = diamond(Q(1, 8), 1)
    base = path[0]
    controls = []

    def refuse(name, expected, *args, **kwargs):
        try:
            bounded(*args, **kwargs)
        except Refusal as exc:
            if str(exc) != expected:
                raise AssertionError((name, expected, str(exc))) from exc
            controls.append({"name": name, "result": str(exc)})
        else:
            raise AssertionError("unrefused control: " + name)

    phrase = "绕零孔 正行 1 周"
    refuse("reversed-path", "DirectionOrTurnMismatch", phrase, path[::-1], base, I)
    refuse("wrong-turns", "DirectionOrTurnMismatch", phrase, diamond(Q(1, 8), 2), base, I)
    refuse("missing-basis", "UnknownBasis", phrase, path, base, None)
    refuse("wrong-action", "ActionMismatch", phrase, path, base, I, claimed=inverse(A))
    refuse("ambiguous-close", "UnsupportedPhrase", "闭合", path, base, I)
    refuse("origin-edge", "OriginOnEdge", phrase, (base, (-base[0], Q(0)), base), base, I)
    outside = diamond(Q(3, 4), 1)
    refuse("outside-disk", "OutsideLocalDisk", phrase, outside, outside[0], I)
    refuse("wrong-base", "WrongBasepoint", phrase, path, (Q(1, 9), Q(0)), I)
    refuse("non-SL-basis", "InvalidBasis", phrase, path, base, ((2, 0), (0, 1)))
    refuse("open-path", "OpenPath", phrase, path[:-1], base, I)
    refuse("oversize-path", "UnknownVertexBudget", phrase, path * 7, base, I)
    refuse("coordinate-budget", "UnknownCoordinateBudget", phrase,
           ((Q(1, 2**65), Q(0)), (Q(1, 2**65), Q(0))), (Q(1, 2**65), Q(0)), I)
    refined = []
    for a, b in zip(path, path[1:]):
        refined.extend((a, tuple((a[i] + b[i]) / 2 for i in range(2))))
    refined.append(base)
    r1 = bounded(phrase, path, base, I)
    r2 = bounded(phrase, tuple(refined), base, I)
    assert r1["action"] == r2["action"] and r1["history"] != r2["history"]
    controls.append({"name": "subdivision", "result": "same action, retained distinct path",
                     "original": r1, "refined": r2})
    b = ((1, 0), (-2, 1))
    commutator = mm(mm(mm(A, b), inverse(A)), inverse(b))
    assert commutator == ((13, 8), (8, 5)) and commutator != I
    controls.append({"name": "global-commutator", "loop_word": ["0+", "1+", "0-", "1-"],
                     "abelian_winding": [0, 0], "matrix_product_left_to_right": commutator,
                     "result": "zero winding pair does not imply global identity",
                     "path_status": "formal word in imported generators, no global polygon supplied"})
    # A locally contractible path is distinguishable from the one-turn instruction.
    cancel = path + path[::-1][1:]
    assert winding(cancel, base) == 0
    refuse("contractible-not-one-turn", "DirectionOrTurnMismatch", phrase, cancel, base, I)
    controls_seconds = time.perf_counter() - control_start
    serialize_start = time.perf_counter()
    wire = json.dumps({"records": records, "controls": controls}, ensure_ascii=False)
    serialization = time.perf_counter() - serialize_start
    replay_start = time.perf_counter()
    reloaded = json.loads(wire)
    calls_before_replay = calls
    if calls_before_replay > contract["budget"]["cases"]:
        raise Refusal("UnknownCaseBudget")
    # Replay consumes the same total call counter and wall deadline.
    for old in reloaded["records"]:
        if time.perf_counter() - start > 30:
            raise Refusal("UnknownRunBudget")
        path_in = tuple(tuple(Q(v) for v in p) for p in old["path"])
        basis_in = tuple(tuple(row) for row in old["basis_columns_in_reference_basis"])
        result = bounded(old["phrase"], path_in, tuple(Q(v) for v in old["basepoint"]), basis_in)
        assert json.loads(json.dumps(result)) == old
    replay_seconds = time.perf_counter() - replay_start
    report = {"status": "FiniteChecksPassed", "base": contract["base"],
              "library": contract["library"], "python": sys.version,
              "contract_sha256": hashlib.sha256(raw_contract).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "baseline_cases": 36, "fresh_reuse_cases": 1,
              "checked_calls_before_replay": calls_before_replay, "total_checked_calls": calls,
              "replay_calls": len(records), "endpoint_identity_false_positives": 37,
              "cost_seconds": {"construction": construction, "verification": verification,
                               "reuse": reuse, "controls": controls_seconds,
                               "serialization": serialization, "replay": replay_seconds,
                               "before_report_write": time.perf_counter() - start},
              "sampled_process_max_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "unmeasured": ["authoring and network", "temporary integer bit maxima",
                             "native execution", "analytic periods", "final report write time"],
              **reloaded}
    if time.perf_counter() - start > 30:
        raise Refusal("UnknownRunBudget")
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "evidence.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("records", "controls")}, indent=2))
    print(json.dumps([{k: v for k, v in c.items() if k not in ("original", "refined")}
                      for c in controls], ensure_ascii=False))


if __name__ == "__main__":
    main()
