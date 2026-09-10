"""Bounded external calibration. No Adva native semantic authority."""
import hashlib
import itertools
import json
import resource
import signal
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
START = time.perf_counter()
CHECKS = 0


def check(ok, label):
    global CHECKS
    CHECKS += 1
    if CHECKS > 100000 or time.perf_counter() - START > 9:
        raise TimeoutError("check or wall budget")
    if not ok:
        raise AssertionError(label)


def mat(rows):
    return [[F(x) for x in row] for row in rows]


def transpose(a):
    return [list(row) for row in zip(*a)]


def mul(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def add(a, b):
    return [[x+y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def scale(a, k):
    return [[x*k for x in row] for row in a]


I = mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
ZERO = scale(I, 0)
P = mat([[F(1, 3)]*3]*3)
Q = add(I, scale(P, -1))
DELTA = scale(Q, 3)


def inverse(a):
    b = [row[:] + identity[:] for row, identity in zip(a, I)]
    for j in range(3):
        pivot = next((i for i in range(j, 3) if b[i][j]), None)
        if pivot is None:
            raise ValueError("SingularTransform")
        b[j], b[pivot] = b[pivot], b[j]
        d = b[j][j]
        b[j] = [v/d for v in b[j]]
        for i in range(3):
            if i != j:
                b[i] = [v-b[i][j]*w for v, w in zip(b[i], b[j])]
    return [row[3:] for row in b]


def energy(x, g):
    return mul(transpose(x), mul(g, x))[0][0]


def partition(x):
    return sorted([i for i, row in enumerate(x) if row[0] == value]
                  for value in {row[0] for row in x})


def packed(obj):
    if isinstance(obj, F):
        return [obj.numerator, obj.denominator]
    if isinstance(obj, dict):
        return {k: packed(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list)):
        return [packed(v) for v in obj]
    return obj


def solve(b, mean, delta, fuel=1, gauge=True):
    if fuel < 1:
        return {"status": "Unknown:Fuel", "remaining": fuel}
    if mul(mean, b) != [[0]]:
        return {"status": "IncompatibleLoad", "obstruction": mul(mean, b)}
    if not gauge:
        return {"status": "Unknown:NonUnique", "residual": "constant-mode family"}
    phi = scale(b, F(1, 3))
    check(mul(delta, phi) == b and mul(mean, phi) == [[0]], "solution and gauge")
    return {"status": "UniqueInDeclaredGauge", "phi": phi}


def trial(contract):
    costs = {}
    t0 = time.perf_counter()
    c = mat(contract["objects"]["C"])
    l = scale(add(scale(I, 2), c), F(1, 3))
    linv = scale(add(add(scale(I, 4), scale(c, -2)), mul(c, c)), F(1, 3))
    mean = mat([[1, 1, 1]])
    frames = {}
    for name, raw in contract["transforms"].items():
        t = mat(raw)
        ti = inverse(t)
        frames[name] = {"T": t, "Ti": ti, "G": mul(transpose(ti), ti),
                        "P": mul(t, mul(P, ti)), "Q": mul(t, mul(Q, ti)),
                        "Delta": mul(t, mul(DELTA, ti)), "L": mul(t, mul(l, ti)),
                        "O": ti, "mean": mul(mean, ti)}
    costs["frame_construction_seconds"] = time.perf_counter()-t0
    t0 = time.perf_counter()
    identities = {"P_idempotent": mul(P, P) == P, "Q_idempotent": mul(Q, Q) == Q,
                  "disjoint": mul(P, Q) == ZERO, "split_merge": add(P, Q) == I,
                  "L_inverse": mul(l, linv) == I and mul(linv, l) == I,
                  "energy": mul(transpose(l), l) == add(P, scale(Q, F(1, 3)))}
    l6 = I
    for _ in range(6):
        l6 = mul(l, l6)
    identities["six_steps"] = l6 == add(P, scale(Q, F(-1, 27)))
    for name, f in frames.items():
        identities[name+"_inverse"] = mul(f["T"], f["Ti"]) == I
        identities[name+"_metric"] = mul(transpose(f["T"]), mul(f["G"], f["T"])) == I
        identities[name+"_observer"] = mul(f["O"], f["T"]) == I
        identities[name+"_split"] = add(f["P"], f["Q"]) == I
        identities[name+"_energy"] = mul(transpose(f["L"]), mul(f["G"], f["L"])) == mul(f["G"], add(f["P"], scale(f["Q"], F(1, 3))))
    for name, ok in identities.items():
        check(ok, name)
    costs["matrix_verification_seconds"] = time.perf_counter()-t0
    rows = []
    for family, inputs in [("grid", list(itertools.product(contract["finite_inputs"]["grid"], repeat=3))),
                           ("fresh", [contract["finite_inputs"]["fresh_vector"]])]:
        t0 = time.perf_counter()
        for name, f in frames.items():
            for values in inputs:
                x = mat([[v] for v in values])
                y = mul(f["T"], x)
                parts = [mul(f["P"], y), mul(f["Q"], y)]
                check(add(*parts) == y, "merge")
                check(parts == [mul(f["T"], mul(P, x)), mul(f["T"], mul(Q, x))], "split covariance")
                check(mul(f["O"], y) == x, "observation")
                check(partition(mul(f["O"], y)) == partition(x), "observed partition")
                check(energy(y, f["G"]) == energy(x, I), "metric")
                a = solve(x, mean, DELTA)
                b = solve(y, f["mean"], f["Delta"])
                check(a["status"] == b["status"], "judgment")
                if "phi" in a:
                    check(mul(f["T"], a["phi"]) == b["phi"], "selected solution")
                tx, ty, history = x, y, []
                for step in range(6):
                    tx, ty = mul(l, tx), mul(f["L"], ty)
                    check(ty == mul(f["T"], tx), "step covariance")
                    check(energy(mul(f["Q"], ty), f["G"]) == energy(mul(Q, x), I)/3**(step+1), "residual energy")
                    history.append({"step": step+1, "source": tx, "target": ty})
                rows.append({"family": family, "frame": name, "input": x, "encoded": y,
                             "parts": parts, "judgment": b, "history": history})
        costs[family+"_construction_and_verification_seconds"] = time.perf_counter()-t0
    check(len(rows) == 84, "coverage")
    t0 = time.perf_counter()
    f = frames["scale"]
    u, v = mat([[1], [-1], [0]]), mat([[1], [1], [-2]])
    yu, yv = mul(f["T"], u), mul(f["T"], v)
    controls = {
        "stale_observer": {"before": partition(v), "naive": partition(yv), "transported": partition(mul(f["O"], yv))},
        "stale_metric": {"before": energy(u, I), "naive": energy(yu, I), "transported": energy(yu, f["G"])},
        "stale_mean": {"before": solve(u, mean, DELTA), "naive": solve(yu, mean, f["Delta"]), "transported": solve(yu, f["mean"], f["Delta"])},
        "zero_fuel": solve(u, mean, DELTA, fuel=0),
        "missing_gauge": solve(u, mean, DELTA, gauge=False),
        "eigenbasis_ambiguity": {"u": u, "v": v, "u_partition": partition(u), "v_partition": partition(v)}}
    check(partition(v) != partition(yv), "observer negative control")
    check(energy(u, I) == 2 and energy(yu, I) == 5, "metric negative control")
    check(controls["stale_mean"]["naive"]["status"] == "IncompatibleLoad", "mean negative control")
    check(controls["zero_fuel"]["status"] == "Unknown:Fuel", "fuel control")
    check(controls["missing_gauge"]["status"] == "Unknown:NonUnique", "gauge control")
    check(mul(DELTA, u) == scale(u, 3) and mul(DELTA, v) == scale(v, 3) and partition(u) != partition(v), "eigenbasis control")
    try:
        inverse(mat([[1, 0, 0], [0, 1, 0], [0, 0, 0]]))
    except ValueError as exc:
        controls["singular"] = str(exc)
    else:
        raise AssertionError("singular matrix accepted")
    costs["controls_seconds"] = time.perf_counter()-t0
    return {"status": "PassedFiniteCalibration", "frames": frames, "identities": identities,
            "rows": rows, "controls": controls, "costs": costs,
            "residual": contract["residual"], "new_native_words": 0}


def main():
    resource.setrlimit(resource.RLIMIT_AS, (256*1024**2, 256*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU, (8, 8))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall budget")))
    signal.alarm(10)
    contract_bytes = (HERE / "contract.json").read_bytes()
    contract = json.loads(contract_bytes)
    try:
        report = packed(trial(contract))
    except (TimeoutError, MemoryError) as exc:
        report = {"status": "Unknown:Budget", "reason": str(exc), "partial_rows": "not checkpointed"}
    except (AssertionError, ValueError) as exc:
        report = {"status": "FailedCheck", "reason": str(exc)}
    report["contract_sha256"] = hashlib.sha256(contract_bytes).hexdigest()
    report["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["logical_checks"] = CHECKS
    report["search_candidates"] = 0
    report["python"] = sys.version
    start = time.perf_counter()
    data = json.dumps(report, sort_keys=True, indent=2).encode()+b"\n"
    if len(data) > 1048576:
        raise RuntimeError("artifact bound")
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_bytes(data)
    write_time = time.perf_counter()-start
    start = time.perf_counter()
    if json.loads(out.read_bytes()) != report:
        raise AssertionError("serialized replay mismatch")
    replay_time = time.perf_counter()-start
    metrics = {"status": report["status"], "logical_checks": CHECKS,
               "rows": len(report.get("rows", [])), "matrix_identities": len(report.get("identities", {})),
               "serialization_and_write_seconds": write_time, "read_and_json_replay_seconds": replay_time,
               "total_before_metrics_write_seconds": time.perf_counter()-START,
               "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               "evidence_sha256": hashlib.sha256(data).hexdigest(), "evidence_bytes": len(data)}
    out.with_suffix(".metrics.json").write_text(json.dumps(metrics, indent=2)+"\n")
    print(json.dumps(metrics))
    return 0 if report["status"] == "PassedFiniteCalibration" else 1


if __name__ == "__main__":
    raise SystemExit(main())
