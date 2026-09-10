"""Exact external calibration; never constructs Adva semantic identities."""
from fractions import Fraction as F
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import resource
import signal
import time

HERE = Path(__file__).resolve().parent
COUNTS = {"assertions": 0, "active_pairs": 0}
LIMITS = {}


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def transpose(a):
    return tuple(zip(*a))


def mv(a, x):
    return tuple(dot(row, x) for row in a)


def mm(a, b):
    return tuple(tuple(dot(row, col) for col in transpose(b)) for row in a)


def determinant(a):
    return a[0][0] * a[1][1] - a[0][1] * a[1][0]


def inverse(a):
    d = determinant(a)
    check(d != 0, "SingularFrame")
    return ((F(a[1][1], d), F(-a[0][1], d)),
            (F(-a[1][0], d), F(a[0][0], d)))


def image(a, points):
    return sorted(mv(a, p) for p in points)


def polar(vertices):
    result = set()
    for a, b in itertools.combinations(vertices, 2):
        COUNTS["active_pairs"] += 1
        if COUNTS["active_pairs"] > LIMITS["max_active_pairs"]:
            raise RuntimeError("Unknown: active-pair budget")
        d = determinant((a, b))
        if not d:
            continue
        point = (F(b[1] - a[1], d), F(a[0] - b[0], d))
        if all(dot(v, point) <= 1 for v in vertices):
            result.add(point)
    return sorted(result)


def multiply(x, y):
    a, b = x
    c, d = y
    return (a * c - b * d, a * d + b * c - b * d)


def conjugate(x):
    a, b = x
    return (a - b, -b)


def real(x):
    return x[0] - F(x[1], 2)


def fixture(name, points, c):
    start = time.perf_counter_ns()
    p = sorted(tuple(map(F, v)) for v in points)
    check(len(p) == 3 and len(set(p)) == 3, "NotTriangle")
    check(tuple(sum(v[i] for v in p) for i in range(2)) == (0, 0), "OriginNotBarycenter")
    check(determinant((p[0], p[1])) != 0, "NotFullDimension")
    # Three non-collinear vertices with strictly positive barycentric origin
    # imply interior origin and a bounded full-dimensional polar.
    q = polar(p)
    check(len(q) == 3, "PolarCoverage")
    check(polar(q) == p, "BipolarMismatch")
    check(all(z.denominator == 1 for v in p + q for z in v), "NotLatticeVertices")
    ct = transpose(inverse(c))
    direct = polar(image(c, p))
    check(direct == image(ct, q), "ConjugationPolarCovariance")
    wrong = 0
    pairs = []
    for x in p:
        for y in q:
            value = dot(x, y)
            transported = dot(mv(c, x), mv(ct, y))
            incorrect = dot(mv(c, x), mv(c, y))
            check(value == transported, "ContragredientPairingMismatch")
            wrong += incorrect != value
            pairs.append({"primal": x, "dual": y, "pairing": value,
                          "correct_transport": transported, "wrong_transport": incorrect})
    check(wrong > 0, "WrongDirectionControlNotDetected")
    return {"name": name, "primal": p, "dual_covector_polar": q,
            "conjugated_primal": image(c, p), "conjugated_primal_polar": direct,
            "bipolar": "Exact", "lattice": "ReflexiveInDeclaredDualLattices",
            "pairings": pairs, "wrong_direction_mismatches": wrong,
            "construction_check_ns": time.perf_counter_ns() - start}


def run(contract):
    start = time.perf_counter_ns()
    o = contract["objects"]
    c = tuple(map(tuple, o["conjugation_C"]))
    g = tuple(tuple(map(F, row)) for row in o["euclidean_gram_G"])
    a = tuple(map(tuple, o["reuse_shear_A"]))
    identity = ((1, 0), (0, 1))
    one, w, w2 = (1, 0), (0, 1), (-1, -1)
    check(multiply(w, w) == w2 and multiply(w2, w) == one, "RootOrder")
    check(tuple(sum(v[i] for v in (one, w, w2)) for i in range(2)) == (0, 0), "RootSum")
    check(multiply(multiply(one, w), w2) == one, "RootProduct")
    check(mm(c, c) == identity and determinant(c) == -1, "ConjugationInvolution")
    check(mm(mm(transpose(c), g), c) == g, "ConjugationNotIsometry")
    check(g[0][0] > 0 and determinant(g) > 0, "GramNotPositiveDefinite")
    grid = list(itertools.product((-1, 0, 1), repeat=2))
    for x in grid:
        check(mv(c, x) == conjugate(x), "CoordinateConjugationMismatch")
        for y in grid:
            check(conjugate(multiply(x, y)) == multiply(conjugate(x), conjugate(y)), "ConjugationProduct")
    formation_ns = time.perf_counter_ns() - start
    first = fixture("cube-root-triangle", o["P"], c)
    second = fixture("unimodular-shear-reuse", image(a, first["primal"]), c)
    check(second["dual_covector_polar"] == image(transpose(inverse(a)), first["dual_covector_polar"]), "ShearPolarMismatch")
    euclidean = image(inverse(g), first["dual_covector_polar"])
    minus_twice = sorted(tuple(-2 * z for z in v) for v in first["primal"])
    check(euclidean == minus_twice, "EuclideanPolarFormula")
    check(first["conjugated_primal"] == first["primal"], "RootSetNotConjugationInvariant")
    check(euclidean != first["conjugated_primal"], "ConjugationConfusedWithPolar")
    check(real(w) == real(w2) and w != w2, "LostProjectionCollision")
    check(real(multiply(w, w)) != real(w) * real(w), "RealProjectionMisreadAsRingMap")
    return {"status": "ExternalExactPass", "native_status": "NotRun",
            "root_sum": [0, 0], "root_product": one,
            "conjugation": c, "dual_transport": transpose(inverse(c)),
            "gram": g, "gram_determinant": determinant(g),
            "root_real_parts": [real(x) for x in (one, w, w2)],
            "euclidean_polar_in_primal_basis": euclidean,
            "real_projection_counterexample": {"left": real(multiply(w, w)), "right": real(w) * real(w)},
            "fixtures": [first, second], "formation_and_ring_checks_ns": formation_ns,
            "construction_and_checks_ns": time.perf_counter_ns() - start,
            "counts": dict(COUNTS)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = (HERE / "contract.json").read_bytes()
    contract = json.loads(data)
    LIMITS.update(contract["budget"])
    resource.setrlimit(resource.RLIMIT_CPU, (LIMITS["cpu_seconds"], LIMITS["cpu_seconds"]))
    resource.setrlimit(resource.RLIMIT_AS, (LIMITS["memory_bytes"], LIMITS["memory_bytes"]))
    resource.setrlimit(resource.RLIMIT_FSIZE, (LIMITS["output_bytes"], LIMITS["output_bytes"]))
    signal.alarm(LIMITS["wall_seconds"])
    report = run(contract)
    report["contract_sha256"] = hashlib.sha256(data).hexdigest()
    report["code_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["rss_high_water_KiB_before_codec"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    start = time.perf_counter_ns()
    encoded = json.dumps(report, default=str, sort_keys=True, indent=2) + "\n"
    # JSON roundtrip only; not a second mathematical implementation.
    decoded = json.loads(encoded)
    check(decoded["status"] == report["status"], "SerializationStatus")
    codec_ns = time.perf_counter_ns() - start
    if len(encoded.encode()) > LIMITS["output_bytes"]:
        raise RuntimeError("Unknown: output budget")
    start = time.perf_counter_ns()
    with args.output.open("x") as output:
        output.write(encoded)
    write_ns = time.perf_counter_ns() - start
    print(json.dumps({"codec_ns": codec_ns, "write_ns": write_ns,
                      "total_assertions_including_codec": COUNTS["assertions"],
                      "output_bytes": len(encoded.encode()),
                      "rss_high_water_KiB_final": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))


if __name__ == "__main__":
    main()
