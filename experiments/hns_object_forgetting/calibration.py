"""Does a graded shadow separate isomorphism classes once the arrow may fold?

The earlier experiment restricted to injective A2 representations, where the
isomorphism class is the dimension pair and the graded data therefore pins the
object. Here injectivity is dropped: the isomorphism class becomes the triple
(dim V1, dim V2, rank of the arrow) while the graded data still records dimension
pairs and slopes. The question is whether two classes then share one shadow, and
if they do, which key loses them.

Every object, subobject and quotient is a finite set of vectors over a prime
field and every slope is an exact Fraction.

Forward: at an exact parameter, the Harder-Narasimhan filtration of every
isomorphism class in the declared range.
Backward: group the graded data and look for collisions between classes.
"""
import itertools
import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
COUNTS = {"assertions": 0, "objects": 0, "subobject_pairs": 0, "filtrations": 0}
LIMITS = {}
DIMS = {}


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


# ------------------------------------------------------- finite field algebra

def vectors(p, d):
    return [tuple(v) for v in itertools.product(range(p), repeat=d)]


def zero(d):
    return tuple([0] * d)


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
    if d == 0:
        S = frozenset({zero(0)})
        DIMS[S] = 0          # the zero space must be registered too
        return [S]
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
    out = sorted(seen, key=lambda s: (len(s), sorted(s)))
    for S in out:
        n, dim = len(S), 0
        while n > 1:
            n //= p
            dim += 1
        DIMS[S] = dim
    return out


def dimof(S):
    if S not in DIMS:
        raise ValueError("DimOfUnregisteredSubspace")
    return DIMS[S]


# -------------------------------------------- the general A2 model over F_p

def image_basis(p, d1, d2, r):
    """The canonical arrow of rank r: e_i -> e_i for i <= r, otherwise 0."""
    gens = [tuple([1 if j == i else 0 for j in range(d2)]) for i in range(r)]
    return span(p, gens, d2)


def slope(dims, theta):
    total = dims[0] + dims[1]
    check(total > 0, "SlopeOfZeroObject")
    return Fr(theta[0] * dims[0] + theta[1] * dims[1], total)


def phi_image(p, U1, d2, r):
    """phi(U1) for the canonical arrow, as a subspace of F_p^d2."""
    gens = []
    for v in U1:
        gens.append(tuple(v[i] if i < r else 0 for i in range(d2)))
    return span(p, gens, d2)


def subobjects(p, d1, d2, r, subs1, subs2):
    """All (U1, U2) with phi(U1) subset U2: the subobjects of this object."""
    out = []
    for U1 in subs1:
        pu = phi_image(p, U1, d2, r)
        for U2 in subs2:
            if pu <= U2:
                out.append((U1, U2))
    COUNTS["subobject_pairs"] += len(out)
    return out


def piece_rank(p, U1, previous_U2, d2, r):
    """Rank of the arrow on the graded piece F_i / F_(i-1).

    The piece's image is (phi(U1_i) + U2_(i-1)) / U2_(i-1), so its rank is
    dim(phi(U1_i) + U2_(i-1)) - dim U2_(i-1). Using the whole object's image and
    the accumulated subobject instead gives the rank of E / F_i, which is a
    different number and is zero for the last piece of every object.
    """
    return (dimof(span(p, list(phi_image(p, U1, d2, r)) + list(previous_U2), d2))
            - dimof(previous_U2))


def hn_filtration(p, d1, d2, r, subs, im_phi, theta):
    """The Harder-Narasimhan filtration, carrying the quotient rank as well."""
    COUNTS["filtrations"] += 1
    Z1, Z2 = frozenset({zero(d1)}), frozenset({zero(d2)})
    current = (Z1, Z2)
    pieces = []
    guard = 0
    while (dimof(current[0]), dimof(current[1])) != (d1, d2):
        guard += 1
        check(guard <= 64, "FiltrationDidNotTerminate")
        cd = (dimof(current[0]), dimof(current[1]))
        candidates = [U for U in subs
                      if U[0] >= current[0] and U[1] >= current[1]
                      and (dimof(U[0]), dimof(U[1])) != cd]
        check(candidates, "NoCandidateAboveCurrent")
        scored = [(slope((dimof(U[0]) - cd[0], dimof(U[1]) - cd[1]), theta), U)
                  for U in candidates]
        best = max(s for s, _ in scored)
        top = [U for s, U in scored if s == best]
        merged = top[0]
        for U in top[1:]:
            merged = (span(p, list(merged[0]) + list(U[0]), d1),
                      span(p, list(merged[1]) + list(U[1]), d2))
        check(merged in subs, "MaximalSlopeSumNotASubobject")
        q = (dimof(merged[0]) - cd[0], dimof(merged[1]) - cd[1])
        check(slope(q, theta) == best, "SumChangedTheSlope")
        pieces.append({"dims": [q[0], q[1]], "slope": str(slope(q, theta)),
                       "piece_rank": piece_rank(p, merged[0], current[1], d2, r)})
        current = merged
    return pieces


def keys_of(pieces):
    dims_slopes = tuple((tuple(pc["dims"]), pc["slope"]) for pc in pieces)
    with_rank = tuple((tuple(pc["dims"]), pc["slope"], pc["piece_rank"]) for pc in pieces)
    return dims_slopes, with_rank


def run(contract):
    o = contract["objects"]
    max_total = o["max_total_dim"]
    max_dim = o["max_ambient_dim"]
    thetas = [tuple(t) for t in o["theta_sweep"]]

    per_field = {}
    collisions = {"dims_and_slopes": [], "dims_slopes_and_piece_rank": []}
    totals = {k: {"colliding_shadows": 0, "max_classes_per_shadow": 0} for k in collisions}
    injective_regression = None

    for p in o["fields"]:
        subs = {d: all_subspaces(p, d) for d in range(0, max_dim + 1)}
        classes = [(d1, d2, r)
                   for d1 in range(0, max_dim + 1) for d2 in range(0, max_dim + 1)
                   for r in range(0, min(d1, d2) + 1)
                   if 1 <= d1 + d2 <= max_total]
        seen_shadow = {"dims_and_slopes": {}, "dims_slopes_and_piece_rank": {}}
        for (d1, d2, r) in classes:
            COUNTS["objects"] += 1
            im_phi = image_basis(p, d1, d2, r)
            subs_here = subobjects(p, d1, d2, r, subs[d1], subs[d2])
            for theta in thetas:
                pieces = hn_filtration(p, d1, d2, r, subs_here, im_phi, theta)
                values = [Fr(pc["slope"]) for pc in pieces]
                for a, b in zip(values, values[1:]):
                    check(a > b, "QuotientSlopesNotStrictlyDecreasing")
                total = sum(pc["dims"][0] + pc["dims"][1] for pc in pieces)
                check(total == d1 + d2, "GradedDimsDoNotSumToTheObject")
                acc = sum(Fr(pc["dims"][0] + pc["dims"][1], d1 + d2) * Fr(pc["slope"])
                          for pc in pieces)
                check(acc == slope((d1, d2), theta), "SlopeConservationFailed")
                for name, key in zip(("dims_and_slopes", "dims_slopes_and_piece_rank"),
                                     keys_of(pieces)):
                    seen_shadow[name].setdefault((theta, key), []).append((d1, d2, r))
            if r == d1 and injective_regression is None and d1 > 0:
                # the injective subfamily must reproduce the earlier result
                groups = {}
                for theta in thetas:
                    pieces = hn_filtration(p, d1, d2, r, subs_here, im_phi, theta)
                    groups.setdefault(keys_of(pieces)[0], set()).add(theta)
                if any(len(v) > 1 for v in groups.values()):
                    injective_regression = {"field": p, "dims": [d1, d2],
                                            "chambers": [sorted(list(x) for x in v) for v in groups.values()]}
        for name, table in seen_shadow.items():
            for (theta, key), owners in table.items():
                distinct = sorted(set(owners))
                if len(distinct) > 1:
                    totals[name]["colliding_shadows"] += 1
                    totals[name]["max_classes_per_shadow"] = max(
                        totals[name]["max_classes_per_shadow"], len(distinct))
                    if len(collisions[name]) < 4:
                        collisions[name].append({
                            "field": p, "parameter": list(theta),
                            "shadow": [list(k) for k in key],
                            "classes": [list(c) for c in distinct],
                        })
        per_field[p] = {"classes": len(classes), "objects": len(classes),
                        "subobject_pairs": COUNTS["subobject_pairs"],
                        "shadows_dims_and_slopes": len({k for (_, k) in seen_shadow["dims_and_slopes"]}),
                        "shadows_with_piece_rank": len({k for (_, k) in seen_shadow["dims_slopes_and_piece_rank"]})}
        COUNTS["subobject_pairs"] = 0

    check(collisions["dims_and_slopes"], "NoCollisionUnderDimsAndSlopes")
    check(injective_regression is not None, "InjectiveSubfamilyDidNotReproduceTheChamber")
    return {
        "status": "ExternalExactPass",
        "native_status": "NotRun",
        "per_field": per_field,
        "collisions_dims_and_slopes": collisions["dims_and_slopes"],
        "collisions_with_piece_rank": collisions["dims_slopes_and_piece_rank"],
        "collision_counts": {k: len(v) for k, v in collisions.items()},
        "collision_totals": totals,
        "injective_regression": injective_regression,
        "counts": dict(COUNTS),
    }


def main():
    contract = json.loads((HERE / "contract.json").read_text())
    LIMITS.update(contract["budget"])
    report = run(contract)
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("status", "collision_counts", "per_field", "counts")}, indent=1))
    print("collision (dims+slopes):",
          json.dumps(report["collisions_dims_and_slopes"][:1])[:400])
    print("collision totals:", json.dumps(report["collision_totals"]))
    print("collision (with rank)  :",
          json.dumps(report["collisions_with_piece_rank"][:1])[:300])


if __name__ == "__main__":
    main()
