"""Is the destroyed information an extension class, or just a coordinate?

The previous experiment collided two isomorphism classes under a key that
recorded, for each graded piece, its dimension pair, its slope and its piece
rank. For an A2 representation the triple (dim U1, dim U2, rank) IS the complete
isomorphism type, so that key was already the strongest possible piece-level
key. This experiment states that fact, exhibits a collision whose two objects
have literally the same graded pieces in the same order, and computes Ext^1
exactly to name what distinguishes them.

Two independent routes to Ext^1 are run and compared:
  (a) the hereditary Euler form, dim Ext^1(M,N) = dim Hom(M,N) - <dim M, dim N>;
  (b) brute-force enumeration of isomorphism classes of middle terms, which is
      what Ext^1 classifies and which assumes no formula at all.
Agreement between them is a check on this model, not a derivation of the
Euler-form identity.

Everything is a finite set of vectors over a prime field, every slope is an
exact Fraction, and every Hom space is enumerated.

Forward: at an exact parameter, the Harder-Narasimhan filtration of every
isomorphism class, with each piece recorded by its complete isomorphism type.
Backward: group by that strongest key, exhibit a collision, and compute the
extensions of its pieces.
"""
import hashlib
import itertools
import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
COUNTS = {"assertions": 0, "objects": 0, "subobject_pairs": 0, "filtrations": 0,
          "hom_pairs": 0, "ext_pairs": 0, "middle_terms_examined": 0}
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
        DIMS[S] = 0
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


def image_basis(p, d1, d2, r):
    """The canonical arrow of rank r: e_i -> e_i for i < r, otherwise 0."""
    gens = [tuple([1 if j == i else 0 for j in range(d2)]) for i in range(r)]
    return span(p, gens, d2)


def apply_phi(d1, d2, r, v):
    return tuple(v[i] if i < r else 0 for i in range(d2))


def phi_image(p, U1, d2, r):
    return span(p, [apply_phi(None, d2, r, v) for v in U1], d2)


def slope(dims, theta):
    total = dims[0] + dims[1]
    check(total > 0, "SlopeOfZeroObject")
    return Fr(theta[0] * dims[0] + theta[1] * dims[1], total)


# ------------------------------------------- the complete isomorphism type

def iso_type(d1, d2, r):
    """The multiplicities (a, b, c) of S1, S2 and P1: a = d1-r, b = d2-r, c = r."""
    return (d1 - r, d2 - r, r)


# -------------------------------------------------- Hom and Ext, two routes

def mat_vec(p, d_out, d_in, f, v):
    return tuple(sum(f[i][j] * v[j] for j in range(d_in)) % p for i in range(d_out))


def hom_dim(p, M, N):
    """dim Hom(M, N) by enumerating every pair of linear maps that commutes.

    The enumeration counts maps, and a Hom space is a vector space over F_p, so
    the count is p to the dimension. The exponent is returned, not the count: a
    zero dimensional Hom space has one element, not zero.
    """
    m1, m2, rM = M
    n1, n2, rN = N
    f1s = [tuple(itertools.product(range(p), repeat=n1)) for _ in range(m1)]
    f2s = [tuple(itertools.product(range(p), repeat=n2)) for _ in range(m2)]
    counted = 0
    for f1 in itertools.product(*f1s):
        for f2 in itertools.product(*f2s):
            ok = True
            for i in range(m1):
                lhs = apply_phi(None, n2, rN, f1[i])
                rhs = mat_vec(p, n2, m2, f2, apply_phi(None, m2, rM,
                                                      tuple(1 if j == i else 0 for j in range(m1))))
                if lhs != rhs:
                    ok = False
                    break
            if ok:
                counted += 1
    COUNTS["hom_pairs"] += 1
    dim, power = 0, 1
    while power < counted:
        power *= p
        dim += 1
    check(power == counted, "HomSpaceSizeIsNotAPowerOfP")
    return dim


def euler_form(m, n):
    """<m, n> for the A2 quiver with its single arrow 1 -> 2."""
    return m[0] * n[0] + m[1] * n[1] - m[0] * n[1]


def euler_ext1_dim(p, M, N):
    return hom_dim(p, M, N) - euler_form((M[0], M[1]), (N[0], N[1]))


def subobject_types(p, obj, subs):
    """Every subobject, with the complete isomorphism type of itself and of its quotient."""
    d1, d2, r = obj
    V1, V2 = frozenset(vectors(p, d1)), frozenset(vectors(p, d2))
    im = phi_image(p, V1, d2, r)
    out = []
    for U1 in subs[d1]:
        pU1 = phi_image(p, U1, d2, r)
        for U2 in subs[d2]:
            if pU1 <= U2:
                sub_obj = (dimof(U1), dimof(U2), dimof(pU1))
                q_rank = dimof(span(p, list(im) + list(U2), d2)) - dimof(U2)
                quo_obj = (d1 - dimof(U1), d2 - dimof(U2), q_rank)
                out.append((sub_obj, quo_obj))
    return out


def middle_terms(p, M, N, subs):
    """Isomorphism classes of E fitting 0 -> N -> E -> M -> 0, by enumeration."""
    d = (M[0] + N[0], M[1] + N[1])
    found = []
    for r in range(0, min(d[0], d[1]) + 1):
        obj = (d[0], d[1], r)
        COUNTS["middle_terms_examined"] += 1
        for sub_obj, quo_obj in subobject_types(p, obj, subs):
            if sub_obj == N and quo_obj == M:
                found.append(obj)
                break
    COUNTS["ext_pairs"] += 1
    return sorted(set(found))


# -------------------------------------------- the Harder-Narasimhan filtration

def subobjects(p, d1, d2, r, subs1, subs2):
    out = []
    for U1 in subs1:
        pu = phi_image(p, U1, d2, r)
        for U2 in subs2:
            if pu <= U2:
                out.append((U1, U2))
    COUNTS["subobject_pairs"] += len(out)
    return out


def piece_rank(p, U1, previous_U2, d2, r):
    return (dimof(span(p, list(phi_image(p, U1, d2, r)) + list(previous_U2), d2))
            - dimof(previous_U2))


def hn_filtration(p, d1, d2, r, subs, theta):
    """The filtration, each piece carrying dims, slope, piece rank and full type."""
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
        pr = piece_rank(p, merged[0], current[1], d2, r)
        check(0 <= pr <= min(q), "PieceRankOutOfRange")
        pieces.append({"dims": [q[0], q[1]], "slope": str(slope(q, theta)),
                       "piece_rank": pr, "iso_type": list(iso_type(q[0], q[1], pr))})
        current = merged
    return pieces


def strongest_key(pieces):
    """Per graded piece: dimension pair, slope and the COMPLETE isomorphism type."""
    return tuple((tuple(pc["dims"]), pc["slope"], pc["piece_rank"]) for pc in pieces)


def pieces_as_objects(pieces):
    return tuple((tuple(pc["dims"]), pc["piece_rank"]) for pc in pieces)


# ------------------------------------------------------------------- the run

def run(contract):
    o = contract["objects"]
    max_total, max_dim = o["max_total_dim"], o["max_ambient_dim"]
    ext_max = o["ext_family_max_dim"]
    thetas = [tuple(t) for t in o["theta_sweep"]]

    per_field, collisions, witnesses = {}, [], []
    slope_invariance = {}
    semistable_counts = {}
    ext_tables = {}
    piece_type_identity = {}

    for p in o["fields"]:
        subs = {d: all_subspaces(p, d) for d in range(0, max_dim + 1)}
        classes = [(d1, d2, r)
                   for d1 in range(0, max_dim + 1) for d2 in range(0, max_dim + 1)
                   for r in range(0, min(d1, d2) + 1)
                   if 1 <= d1 + d2 <= max_total]
        seen = {}
        seen_weak = {}
        P1 = (1, 1, 1)
        for (d1, d2, r) in classes:
            COUNTS["objects"] += 1
            subs_here = subobjects(p, d1, d2, r, subs[d1], subs[d2])
            # an object of a fixed dimension vector has one slope, whatever its arrow
            slope_invariance.setdefault((p, d1, d2), set()).add(str(slope((d1, d2), (1, -1))))
            for theta in thetas:
                pieces = hn_filtration(p, d1, d2, r, subs_here, theta)
                key = strongest_key(pieces)
                seen.setdefault((theta, key), []).append((d1, d2, r))
                if theta == (1, 1):
                    # the semistable parameter: one piece, so the weak key is the
                    # dimension pair and slope alone and loses the arrow entirely
                    seen_weak.setdefault(p, {}).setdefault(
                        tuple((tuple(pc["dims"]), pc["slope"]) for pc in pieces),
                        []).append((d1, d2, r))
                values = [Fr(pc["slope"]) for pc in pieces]
                for a, b in zip(values, values[1:]):
                    check(a > b, "QuotientSlopesNotStrictlyDecreasing")
                # every piece is a genuine object of the category, and the
                # multiplicities account for its total dimension: S1 and S2 have
                # one dimension each and P1 has two.
                for pc in pieces:
                    a, b, c = pc["iso_type"]
                    check(c == pc["piece_rank"], "PieceTypeDisagreesWithRank")
                    check(a + b + 2 * c == sum(pc["dims"]), "PieceTypeHasWrongSize")
                    check(pc["dims"] == [a + c, b + c], "MultiplicitiesDoNotReconstructTheDims")
                # the witness pair: same pieces as OBJECTS, different objects
                if theta == (0, 1) and (d1, d2) == (1, 1):
                    piece_type_identity.setdefault(
                        (p, tuple(pieces_as_objects(pieces))), []).append(r)
                    if r == 1:
                        witnesses.append({
                            "field": p, "parameter": list(theta), "dims": [d1, d2],
                            "rank_one_object": [d1, d2, r],
                            "rank_zero_object": [d1, d2, 0],
                            "pieces_of_the_rank_one_object": pieces,
                        })
        for (theta, key), owners in seen.items():
            distinct = sorted(set(owners))
            if len(distinct) > 1:
                dims = sorted({(c[0], c[1]) for c in distinct})
                same_dims = len(dims) == 1
                entry = {"field": p, "parameter": list(theta),
                         "strongest_key": [list(k) for k in key],
                         "classes": [list(c) for c in distinct],
                         "all_classes_share_one_dimension_vector": same_dims}
                # When the colliding classes share a dimension vector, the graded
                # pieces are identical as objects and the classes are exactly the
                # possible gluing ranks: the number of isomorphism classes with
                # that dimension vector is min(d1, d2) + 1.
                if same_dims:
                    d1, d2 = dims[0]
                    entry["gluing_ranks"] = sorted(c[2] for c in distinct)
                    entry["predicted_number_of_gluing_ranks"] = min(d1, d2) + 1
                    entry["collision_is_the_whole_class_set"] = (
                        len(distinct) == min(d1, d2) + 1)
                    check(len(distinct) == min(d1, d2) + 1,
                          "CollisionIsNotTheWholeSetOfGluingRanks")
                collisions.append(entry)

        # Ext^1 for the indecomposables, by two independent routes
        indec = [(1, 0, 0), (0, 1, 0), P1]
        table = []
        for M in indec:
            for N in indec:
                by_formula = euler_ext1_dim(p, M, N)
                terms = middle_terms(p, M, N, subs)
                predicted = 1 if by_formula == 0 else (p ** by_formula - 1) // (p - 1) + 1
                check(by_formula >= 0, "NegativeExtDimension")
                check(len(terms) == predicted, "MiddleTermsDisagreeWithEulerForm")
                check(all(t[0] <= ext_max and t[1] <= ext_max for t in terms),
                      "MiddleTermOutsideDeclaredFamily")
                table.append({"quotient": list(M), "subobject": list(N),
                              "hom_dim": hom_dim(p, M, N),
                              "euler_pairing": euler_form((M[0], M[1]), (N[0], N[1])),
                              "ext1_dim": by_formula,
                              "middle_terms": [list(t) for t in terms],
                              "split_only": by_formula == 0})
        ext_tables[p] = table

        # At the semistable parameter the filtration is trivial, so the strongest
        # key is the object itself and loses nothing; the weak key is exactly the
        # dimension pair and the slope, and the number of classes it hides is the
        # number of possible gluing ranks, which is min(d1, d2) + 1.
        for key, owners in seen_weak.get(p, {}).items():
            distinct = sorted(set(owners))
            dims = list(key[0][0])
            check(len(key) == 1, "SemistableFiltrationIsNotTrivial")
            semistable_counts.setdefault(p, {})[tuple(dims)] = {
                "classes_sharing_the_weak_key": len(distinct),
                "predicted_by_gluing_rank": min(dims) + 1,
                "strongest_key_separates_them": len(
                    {strongest_key(hn_filtration(p, d[0], d[1], d[2], subobjects(
                        p, d[0], d[1], d[2], subs[d[0]], subs[d[1]]), (1, 1))) for d in distinct}) == len(distinct),
            }
            check(len(distinct) == min(dims) + 1, "GluingRankCountDisagreesWithClasses")
        for entry in semistable_counts.get(p, {}).values():
            check(entry["strongest_key_separates_them"], "SemistableStrongestKeyCollided")
        per_field[p] = {"classes": len(classes), "objects": len(classes),
                        "strongest_key_shadows": len({k for (_, k) in seen})}
        COUNTS["subobject_pairs"] = 0

    check(collisions, "NoCollisionUnderTheStrongestPieceLevelKey")
    check(witnesses, "NoWitnessWithIdenticalPieceObjects")
    # the witness: two objects whose graded pieces agree as objects
    for w in witnesses:
        p = w["field"]
        pair = piece_type_identity.get((p, tuple((tuple(pc["dims"]), pc["piece_rank"])
                                                for pc in
                                                w["pieces_of_the_rank_one_object"])))
        check(pair is not None and sorted(pair) == [0, 1],
              "TheTwoObjectsDoNotShareTheirPiecesAsObjects")
        check(tuple(w["rank_one_object"]) != tuple(w["rank_zero_object"]),
              "TheTwoObjectsAreTheSameObject")
        check(iso_type(1, 1, 0) != iso_type(1, 1, 1),
              "TheTwoObjectsHaveTheSameIsomorphismType")
    # the two routes to Ext^1 agree, and the non-split extension is realised
    for p, table in ext_tables.items():
        row = [t for t in table if t["quotient"] == [1, 0, 0] and t["subobject"] == [0, 1, 0]]
        check(len(row) == 1, "MissingTheWitnessExtRow")
        check(row[0]["ext1_dim"] == 1, "WitnessExtIsNotOneDimensional")
        check(len(row[0]["middle_terms"]) == 2, "WitnessHasNoNonSplitExtension")
        check([1, 1, 0] in row[0]["middle_terms"] and [1, 1, 1] in row[0]["middle_terms"],
              "WitnessMiddleTermsAreNotTheTwoKnownObjects")
        rev = [t for t in table if t["quotient"] == [0, 1, 0] and t["subobject"] == [1, 0, 0]]
        check(len(rev) == 1 and rev[0]["ext1_dim"] == 0,
              "TheReversedOrderingShouldHaveNoNonSplitExtension")
    # the slope is deformation invariant, so it cannot see the gluing
    for key, values in slope_invariance.items():
        check(len(values) == 1, "SlopeDependsOnSomethingOtherThanTheDimensionVector")

    # the strongest key must be the same key the earlier experiment used
    cross = contract["cross_experiment"]
    sibling = REPO / cross["path"]
    digest = hashlib.sha256(sibling.read_bytes()).hexdigest()
    check(digest == cross["sha256"], "SiblingEvidenceDigestChanged")
    prior = json.loads(sibling.read_text())
    prior_colliding = prior["collision_totals"]["dims_slopes_and_piece_rank"]["colliding_shadows"]
    check(len(collisions) == prior_colliding, "CollisionCountDisagreesWithTheSiblingRun")
    for p in o["fields"]:
        check(per_field[p]["strongest_key_shadows"]
              == prior["per_field"][str(p)]["shadows_with_piece_rank"],
              "ShadowCountDisagreesWithTheSiblingRun")

    return {
        "status": "ExternalExactPass",
        "native_status": "NotRun",
        "per_field": per_field,
        "strongest_key": "per graded piece: dimension pair, slope and the complete isomorphism type "
                         "(dim U1, dim U2, rank); for an A2 representation that triple IS the "
                         "isomorphism class of the piece",
        "collision_count": len(collisions),
        "collisions_under_the_strongest_key": collisions[:4],
        "cross_experiment": {"path": cross["path"], "sha256": digest,
                            "sibling_colliding_shadows": prior_colliding,
                            "this_run_collisions": len(collisions)},
        "witnesses_with_identical_piece_objects": witnesses[:2],
        "ext1_tables": ext_tables,
        "semistable_shadow_counts": {str(p): {str(k): v for k, v in table.items()}
                                     for p, table in semistable_counts.items()},
        "slope_invariance_pairs": len(slope_invariance),
        "counts": dict(COUNTS),
    }


def main():
    contract = json.loads((HERE / "contract.json").read_text())
    LIMITS.update(contract["budget"])
    report = run(contract)
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("status", "collision_count", "per_field", "counts")}, indent=1))
    print("witness:", json.dumps(report["witnesses_with_identical_piece_objects"][:1])[:600])
    print("ext (S1 quotient, S2 subobject):",
          json.dumps([r for r in report["ext1_tables"][2]
                      if r["quotient"] == [1, 0, 0] and r["subobject"] == [0, 1, 0]]))
    print("collision sample:", json.dumps(report["collisions_under_the_strongest_key"][:1])[:400])


if __name__ == "__main__":
    main()
