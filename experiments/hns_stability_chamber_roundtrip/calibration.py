"""Forward and backward across a Harder-Narasimhan filtration, exactly.

Carrier: an injective representation of A2 = (1 -> 2) over F_p, realised as a
subspace pair V1 subset V2 inside F_p^d. Every object, subobject and quotient is
a finite set of vectors over a prime field and every slope is an exact Fraction,
so nothing here samples or approximates.

Forward: at an exact stability parameter theta, compute the Harder-Narasimhan
filtration and its graded data.

Backward: from the graded data alone, ask what produced it. Two distinct
forgettings are measured, and they are different questions:
  (a) for a fixed object, which parameters give this graded data;
  (b) for a fixed parameter, which objects give this graded data.
The residual kept by this experiment is whichever of the two is many-to-one.
"""
import itertools
import json
import pathlib
import sys
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
COUNTS = {"assertions": 0, "carriers": 0, "subobject_pairs": 0, "filtrations": 0}
LIMITS = {}


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


# ------------------------------------------------------- finite field algebra

def vectors(p, d):
    return [tuple(v) for v in itertools.product(range(p), repeat=d)]


ZERO_CACHE = {}


def zero(d):
    if d not in ZERO_CACHE:
        ZERO_CACHE[d] = tuple([0] * d)
    return ZERO_CACHE[d]


def add(p, u, v):
    return tuple((a + b) % p for a, b in zip(u, v))


def span(p, generators, d):
    S = {zero(d)}
    changed = True
    while changed:
        changed = False
        for v in list(S):
            for g in generators:
                w = add(p, v, g)
                if w not in S:
                    S.add(w)
                    changed = True
    return frozenset(S)


def all_subspaces(p, d):
    pool = [v for v in vectors(p, d) if any(v)]
    seen, frontier = set(), [span(p, [], d)]
    while frontier:
        S = frontier.pop()
        if S in seen:
            continue
        seen.add(S)
        for v in pool:
            T = span(p, list(S) + [v], d)
            if T not in seen:
                frontier.append(T)
    return sorted(seen, key=lambda s: (len(s), sorted(s)))


# ------------------------------------------------------------- the A2 model

DIMS = {}


def register_dims(p, spaces):
    """Cache the dimension of every enumerated subspace.

    `len(S)` is the number of vectors, which is p**dim and not the dimension.
    This is a structural lookup on a hot path, so it is cached rather than
    counted as an assertion.
    """
    for S in spaces:
        n, dim = len(S), 0
        while n > 1:
            n //= p
            dim += 1
        DIMS[S] = dim


def dimof(p, S):
    if S not in DIMS:
        raise ValueError("DimOfUnregisteredSubspace")
    return DIMS[S]


def slope(dims, theta):
    d1, d2 = dims
    total = d1 + d2
    check(total > 0, "SlopeOfZeroObject")
    return F(theta[0] * d1 + theta[1] * d2, total)


def subobjects(p, V1, V2, subs_of):
    """All (U1, U2) with U1 subset U2, U1 subset V1, U2 subset V2."""
    inner = [S for S in subs_of if S <= V2]
    out = [(U1, U2) for U2 in inner for U1 in inner if U1 <= U2 and U1 <= V1]
    COUNTS["subobject_pairs"] += len(out)
    return out


def over(p, U, base):
    return U[0] >= base[0] and U[1] >= base[1]


def quotient_dims(p, U, base):
    return dimof(p, U[0]) - dimof(p, base[0]), dimof(p, U[1]) - dimof(p, base[1])


def hn_filtration(p, carrier, subs, d, theta):
    """The Harder-Narasimhan filtration by the iterated maximal-slope rule."""
    COUNTS["filtrations"] += 1
    Z = frozenset({zero(d)})
    current = (Z, Z)
    pieces = []
    guard = 0
    while current != carrier:
        guard += 1
        check(guard <= 64, "FiltrationDidNotTerminate")
        candidates = [U for U in subs if over(p, U, current) and U != current]
        check(candidates, "NoCandidateAboveCurrent")
        scored = [(slope(quotient_dims(p, U, current), theta), U) for U in candidates]
        best = max(s for s, _ in scored)
        top = [U for s, U in scored if s == best]
        merged = top[0]
        for U in top[1:]:
            merged = (span(p, list(merged[0]) + list(U[0]), d),
                      span(p, list(merged[1]) + list(U[1]), d))
        # the maximal-slope class is closed under sum, so its sum is the maximal member
        check(merged in subs, "MaximalSlopeSumNotASubobject")
        check(slope(quotient_dims(p, merged, current), theta) == best, "SumChangedTheSlope")
        for U in top:
            check(over(p, merged, U), "SumDoesNotContainAMember")
        q = quotient_dims(p, merged, current)
        pieces.append({"dims": [q[0], q[1]], "slope": str(slope(q, theta))})
        current = merged
    return pieces


def graded_key(pieces):
    return tuple((tuple(pc["dims"]), pc["slope"]) for pc in pieces)


def run(contract):
    o = contract["objects"]
    max_dim = o["max_ambient_dim"]
    thetas = [tuple(t) for t in o["theta_sweep"]]
    degenerate = [tuple(t) for t in o["degenerate_theta"]]

    per_field = {}
    wall_pairs = []
    parameter_witnesses = []
    chamber_partitions = []

    for p in o["fields"]:
        subs_cache = {d: all_subspaces(p, d) for d in range(1, max_dim + 1)}
        for d in subs_cache:
            register_dims(p, subs_cache[d])
        carriers = []
        seen_iso = set()
        for d in o["ambient_dims"]:
            spaces = subs_cache[d]
            for V2 in spaces:
                if dimof(p, V2) == 0:
                    continue           # the zero object has no slope
                for V1 in [S for S in spaces if S <= V2]:
                    # An injective A2 representation is classified by its
                    # dimension pair, so embedded copies of one class are one
                    # object. Enumerating embeddings without this made the same
                    # object look like several and produced a spurious
                    # object-forgetting witness.
                    key = (dimof(p, V1), dimof(p, V2))
                    if key in seen_iso:
                        continue
                    seen_iso.add(key)
                    carriers.append((d, V1, V2))
        chamber_sizes = []
        distinct_graded = set()
        degenerate_checks = 0
        by_param = {}
        for (d, V1, V2) in carriers:
            COUNTS["carriers"] += 1
            subs = subobjects(p, V1, V2, subs_cache[d])
            e_dims = (dimof(p, V1), dimof(p, V2))
            per_carrier = {}
            for theta in thetas:
                pieces = hn_filtration(p, (V1, V2), subs, d, theta)
                key = graded_key(pieces)
                per_carrier[theta] = key
                distinct_graded.add(key)
                by_param.setdefault(theta, {}).setdefault(key, []).append((p, d, e_dims))
                values = [F(pc["slope"]) for pc in pieces]
                for a, b in zip(values, values[1:]):
                    check(a > b, "QuotientSlopesNotStrictlyDecreasing")
                total = sum(pc["dims"][0] + pc["dims"][1] for pc in pieces)
                check(total == e_dims[0] + e_dims[1], "GradedDimsDoNotSumToTheObject")
                acc = sum(F(pc["dims"][0] + pc["dims"][1], e_dims[0] + e_dims[1])
                          * F(pc["slope"]) for pc in pieces)
                check(acc == slope(e_dims, theta), "SlopeConservationFailed")
            # (a) parameter forgetting, for this object
            groups = {}
            for theta, key in per_carrier.items():
                groups.setdefault(key, set()).add(theta)
            chamber_sizes.extend(len(v) for v in groups.values())
            for key, thetas_with_key in groups.items():
                if len(thetas_with_key) > 1:
                    parameter_witnesses.append({
                        "field": p, "ambient_dim": d, "dims": list(e_dims),
                        "nondegenerate": e_dims[0] > 0 and e_dims[1] > 0,
                        "graded": [list(k) for k in key],
                        "parameters": [list(t) for t in sorted(thetas_with_key)],
                    })
            if e_dims[0] > 0 and e_dims[1] > 0 and len(groups) > 1:
                chamber_partitions.append({
                    "field": p, "ambient_dim": d, "dims": list(e_dims),
                    "chambers": sorted((sorted(list(x) for x in v) for v in groups.values()),
                                       key=lambda c: c[0]),
                })
            # degenerate parameter: every nonzero subobject has one slope
            for theta in degenerate:
                pieces = hn_filtration(p, (V1, V2), subs, d, theta)
                check(len(pieces) == 1 and pieces[0]["dims"] == list(e_dims),
                      "DegenerateParameterIsNotSemistable")
                degenerate_checks += 1
        # (b) object forgetting, for each parameter
        for theta, by_key in by_param.items():
            for key, objects in by_key.items():
                # For a fixed parameter the graded dimensions sum to the
                # object's dimension vector, so this must be one object per key.
                check(len(objects) == 1, "TwoIsomorphismClassesSharedGradedData")
        # walls inside the grid, on the first carrier
        d0, V10, V20 = carriers[0]
        subs0 = subobjects(p, V10, V20, subs_cache[d0])
        prev = None
        for theta in thetas:
            key = graded_key(hn_filtration(p, (V10, V20), subs0, d0, theta))
            if prev is not None and key != prev[1]:
                wall_pairs.append({"field": p, "ambient_dim": d0,
                                   "between": [list(prev[0]), list(theta)]})
            prev = (theta, key)
        per_field[p] = {
            "carriers": len(carriers),
            "subobject_pairs": COUNTS["subobject_pairs"],
            "distinct_graded_data": len(distinct_graded),
            "max_sweep_parameters_per_object": len(thetas),
            "largest_chamber": max(chamber_sizes) if chamber_sizes else 0,
            "degenerate_checks": degenerate_checks,
        }
        COUNTS["subobject_pairs"] = 0

    def best(witnesses):
        strong = [w for w in witnesses if w["nondegenerate"]]
        return (strong[0] if strong else (witnesses[0] if witnesses else None),
                bool(strong))

    parameter_forgetting_witness, param_strong = best(parameter_witnesses)
    check(parameter_forgetting_witness is not None, "NoParameterForgetting")
    check(wall_pairs, "NoWallFoundInsideTheGrid")

    return {
        "status": "ExternalExactPass",
        "native_status": "NotRun",
        "per_field": per_field,
        "parameter_forgetting_witness": parameter_forgetting_witness,
        "parameter_witness_is_nondegenerate": param_strong,
        "parameter_witness_count": len(parameter_witnesses),
        "object_map_is_injective": True,
        "distinct_iso_classes": sum(v["carriers"] for v in per_field.values()),
        "sample_chamber_partition": chamber_partitions[0] if chamber_partitions else None,
        "chamber_partition_count": len(chamber_partitions),
        "wall_count": len(wall_pairs),
        "wall_pairs": wall_pairs[:6],
        "counts": dict(COUNTS),
    }


def main():
    contract = json.loads((HERE / "contract.json").read_text())
    LIMITS.update(contract["budget"])
    report = run(contract)
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("status", "wall_count", "counts", "per_field")}, indent=1))
    print("parameter forgetting:", json.dumps(report["parameter_forgetting_witness"])[:300])
    print("object map injective:", report["object_map_is_injective"],
          "on", report["distinct_iso_classes"], "classes")


if __name__ == "__main__":
    main()
