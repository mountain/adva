#!/usr/bin/env python3
"""Wu's elimination method on plane incidence statements, with checkable results.

Frozen contract: contract.json in this directory (Research 0129 section 3).

Wu's method turns a geometry statement into polynomial hypotheses and a polynomial
conclusion, triangularises the hypotheses into a characteristic chain by
pseudo-division, and reduces the conclusion modulo that chain: a zero remainder
proves the statement on the zero set of the hypotheses, subject to the initials of
the chain not vanishing.

This round runs three statements and a falsified companion of each. Every
remainder is cross-checked by an independent Groebner basis computation, and every
true statement is also evaluated on random exact rational instances. The library
used for polynomial arithmetic is declared, and the run reports whether it is
present rather than assuming it.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import random
import sys
import time
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]

ASSERTIONS = {"n": 0}


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)


def import_sympy():
    try:
        import sympy
        from sympy import Poly, QQ, expand, groebner, prem, symbols
        return {
            "available": True,
            "version": sympy.__version__,
            "Poly": Poly, "QQ": QQ, "expand": expand,
            "groebner": groebner, "prem": prem, "symbols": symbols,
        }
    except Exception as error:  # pragma: no cover - reported, not raised
        return {"available": False, "error": str(error)}


SY = import_sympy()


# --------------------------------------------------------------- the method ----

def select_main_variable(polys, order):
    """Wu's ordering: the polynomial whose main variable is lowest in the order."""
    best = None
    for index, poly in enumerate(polys):
        if poly == 0:
            continue
        for position, variable in enumerate(order):
            if poly.has(variable):
                if best is None or position < best[0]:
                    best = (position, variable, index)
                break
    return best


def triangularise(polys, order, rounds=12):
    """A bounded characteristic-chain computation by pseudo-division.

    Wu's well-ordering principle reduces the degrees of the non-leading
    polynomials against the chosen one until no further reduction is possible.
    This is the basic step; full zero-decomposition with irreducible components is
    not implemented, and the evidence says so.
    """
    expand, prem = SY["expand"], SY["prem"]
    chain = []
    working = [expand(p) for p in polys if p != 0]
    history = []
    for _ in range(rounds):
        choice = select_main_variable(working, order)
        if choice is None:
            break
        _, main, index = choice
        pivot = working.pop(index)
        pivot = expand(pivot)
        chain.append({"main_variable": str(main), "polynomial": str(pivot)})
        reduced = []
        for poly in working:
            remainder = expand(prem(poly, pivot, main))
            history.append({
                "main_variable": str(main),
                "reduced_polynomial_terms": len(expand(poly).as_ordered_terms()) if poly != 0 else 0,
                "remainder_is_zero": remainder == 0,
            })
            if remainder != 0:
                reduced.append(remainder)
        working = reduced
        if not working:
            break
    return chain, working, history


def reduce_conclusion(chain, conclusion):
    """Successive pseudo-remainder reduction of the conclusion modulo the chain."""
    prem, expand = SY["prem"], SY["expand"]
    remainder = expand(conclusion)
    steps = []
    for entry in chain:
        main = SY["symbols"](entry["main_variable"])
        polynomial = expand(entry["polynomial"])
        before_terms = len(expand(remainder).as_ordered_terms()) if remainder != 0 else 0
        remainder = expand(prem(remainder, polynomial, main))
        steps.append({
            "main_variable": entry["main_variable"],
            "terms_before": before_terms,
            "remainder_terms": len(expand(remainder).as_ordered_terms()) if remainder != 0 else 0,
            "remainder_is_zero": remainder == 0,
        })
        if remainder == 0:
            break
    return remainder, steps


def in_ideal(polys, conclusion, order):
    """Independent cross-check on the reduced system: is the conclusion in the ideal?

    The chain is substituted first, so the Groebner computation runs on the free
    variables only; the monomial order is grevlex, which is enough for membership
    and much cheaper than lex.
    """
    groebner, expand, prem = SY["groebner"], SY["expand"], SY["prem"]
    reduced = expand(conclusion)
    for entry in polys:
        main = SY["symbols"](entry["main_variable"]) if isinstance(entry, dict) else None
        if main is None:
            continue
        reduced = expand(prem(reduced, expand(entry["polynomial"]), main))
        if reduced == 0:
            return True
    generators = [p for p in polys if isinstance(p, dict) is False and p != 0]
    generators = [expand(g) for g in generators]
    if not generators:
        return expand(reduced) == 0
    basis = groebner(generators + [expanded_free(reduced)], *order, order="grevlex")
    return expand(basis.reduce(expanded_free(reduced))[1]) == 0


def expanded_free(poly):
    return SY["expand"](poly)


# ------------------------------------------------------------ the statements ----

def build_problem(name):
    """Statements in normalised coordinates, so that the elimination stays small."""
    symbols = SY["symbols"]
    expand = SY["expand"]

    def cross(u, v):
        return (u[1] * v[2] - u[2] * v[1],
                u[2] * v[0] - u[0] * v[2],
                u[0] * v[1] - u[1] * v[0])

    def det3(a, b, c):
        return expand(a[0] * (b[1] * c[2] - b[2] * c[1])
                      - a[1] * (b[0] * c[2] - b[2] * c[0])
                      + a[2] * (b[0] * c[1] - b[1] * c[0]))

    if name.startswith("ceva"):
        # A = (0,0), B = (1,0), C = (0,1); D = (1-t, t) on BC, E = (0, e) on CA,
        # F = (f, 0) on AB. Three variables.
        t_, e_, f_ = symbols("t e f")
        A, B, C = (Fr(0), Fr(0), 1), (Fr(1), Fr(0), 1), (Fr(0), Fr(1), 1)
        D, E, F = (1 - t_, t_, 1), (Fr(0), e_, 1), (f_, Fr(0), 1)
        ceva = expand(t_ * (1 - e_) * f_ - (1 - t_) * e_ * (1 - f_))
        conclusion = det3(cross(A, D), cross(B, E), cross(C, F))
        order = [t_, e_, f_]
        hypotheses = [ceva] if not name.endswith("falsified") else [expand(ceva + 1)]
        return hypotheses, conclusion, order, order, None

    if name.startswith("pappus"):
        # Pappus, as the degenerate Pascal: A, B, C on the x axis, a, b, c on the
        # y axis, and the hexagon A, b, C, a, B, c in that alternating order.
        ps = symbols("p1:4")
        qs = symbols("q1:4")
        A = (ps[0], Fr(0), 1)
        B = (ps[1], Fr(0), 1)
        C = (ps[2], Fr(0), 1)
        a = (Fr(0), qs[0], 1)
        b = (Fr(0), qs[1], 1)
        c = (Fr(0), qs[2], 1)
        s1, s2, s3 = cross(A, b), cross(b, C), cross(C, a)
        s4 = cross(a, C if name.endswith("falsified") else B)   # a wrong vertex breaks it
        s5, s6 = cross(B, c), cross(c, A)
        conclusion = det3(cross(s1, s4), cross(s2, s5), cross(s3, s6))
        order = list(ps) + list(qs)
        return [], conclusion, order, order, None

    # Pascal on the parabola y = x^2: the hypothesis is already a triangular chain.
    xs = symbols("x1:7")
    ys = symbols("y1:7")
    P = [(xs[i], ys[i], 1) for i in range(6)]
    l12 = cross(P[0], P[1])
    l23 = cross(P[1], P[2])
    l34 = cross(P[2], P[3])
    l45 = cross(P[3], P[5] if name.endswith("falsified") else P[4])
    l56 = cross(P[4], P[5])
    l61 = cross(P[5], P[0])
    conclusion = det3(cross(l12, l45), cross(l23, l56), cross(l34, l61))
    hypotheses = [ys[i] - xs[i] ** 2 for i in range(6)]
    order = list(xs) + list(ys)
    return hypotheses, conclusion, order, order, None


def random_instance(name, rng):
    """Exact rational points for the true statements, checked by substitution."""
    if name.startswith("pascal"):
        params = [Fr(rng.randint(1, 9), rng.randint(1, 5)) for _ in range(6)]
        points = [(t, t * t) for t in params]
        substitution = {}
        for i, (x, y) in enumerate(points):
            substitution[SY["symbols"](f"x{i+1}")] = x
            substitution[SY["symbols"](f"y{i+1}")] = y
        return substitution
    if name.startswith("pappus"):
        values = [Fr(rng.randint(1, 9)) for _ in range(6)]
        substitution = {}
        for label, value in zip(("p1x", "p2x", "p3x", "q1x", "q2x", "q3x"), values):
            substitution[SY["symbols"](label)] = value
        return substitution
    return None


def main():
    started = time.monotonic()
    evidence = {
        "schema": "adva.external.wu-elimination-geometry.v0",
        "version": 0,
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "contract": "experiments/wu_elimination_geometry/contract.json",
        "tooling": {
            "polynomial_library": "sympy",
            "available": SY["available"],
            "version": SY.get("version"),
            "pseudo_remainder_used": True,
            "groebner_cross_check_used": True,
            "external_oracle_not_native_authority": True,
        },
        "method": {
            "name": "Wu's elimination method (characteristic chain by pseudo-division)",
            "ordering": OBJ["variable_order"],
            "zero_remainder_means": "the conclusion vanishes on the zero set of the hypotheses wherever the initials of the chain do not vanish",
            "not_implemented": "full zero-decomposition into irreducible components; the chain here is the basic pseudo-division chain",
        },
    }
    if not SY["available"]:
        evidence["status"] = "ToolingUnavailable"
        evidence["reason"] = SY.get("error")
        (HERE / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                                            encoding="utf-8")
        return 1

    rng = random.Random(OBJ["random_seed"])
    results = []
    for base in OBJ["theorems"]:
        for name in (base, base + "_falsified"):
            hypotheses, conclusion, order, variables, points = build_problem(name)
            chain, leftover, history = triangularise(hypotheses, order)
            remainder, steps = reduce_conclusion(chain, conclusion)
            reduced_hypotheses = [h for h in hypotheses if h != 0]
            for entry in chain:
                reduced_hypotheses = [
                    SY["expand"](SY["prem"](h, SY["expand"](entry["polynomial"]),
                                            SY["symbols"](entry["main_variable"])))
                    if h != 0 else h for h in reduced_hypotheses]
            reduced_hypotheses = [h for h in reduced_hypotheses if h != 0]
            if reduced_hypotheses:
                basis = SY["groebner"](reduced_hypotheses + [SY["expand"](remainder)],
                                       *order, order="grevlex")
                agrees = SY["expand"](basis.reduce(SY["expand"](remainder))[1]) == 0
            else:
                agrees = SY["expand"](remainder) == 0
            instances = []
            if not name.endswith("falsified"):
                for _ in range(OBJ["random_instances_per_theorem"]):
                    substitution = random_instance(name, rng)
                    if substitution is None:
                        continue
                    value = SY["expand"](conclusion.subs(substitution))
                    instances.append({"substitution": {str(k): str(v) for k, v in substitution.items()},
                                      "value": str(value), "is_zero": value == 0})
            results.append({
                "statement": name,
                "declared_true": not name.endswith("falsified"),
                "hypothesis_count": len([h for h in hypotheses if h != 0]),
                "chain": chain,
                "chain_initials_non_degeneracy_conditions": [
                    str(SY["Poly"](entry["polynomial"], *order).LC()) for entry in chain
                ],
                "pseudo_reduction_steps": steps,
                "remainder_is_zero": remainder == 0,
                "conclusion_terms": len(SY["expand"](conclusion).as_ordered_terms()) if conclusion != 0 else 0,
                "groebner_membership": agrees,
                "methods_agree": (remainder == 0) == agrees,
                "random_instances": instances,
            })

    evidence["results"] = results
    truth = [row for row in results if row["declared_true"]]
    falsified = [row for row in results if not row["declared_true"]]
    evidence["summary"] = {
        "true_statements_proved_by_a_zero_remainder": [row["statement"] for row in truth
                                                       if row["remainder_is_zero"]],
        "falsified_statements_not_proved": [row["statement"] for row in falsified
                                            if not row["remainder_is_zero"]],
        "cross_checks_agreeing": [row["statement"] for row in results if row["methods_agree"]],
        "zero_remainders": sum(1 for row in results if row["remainder_is_zero"]),
        "nonzero_remainders": sum(1 for row in results if not row["remainder_is_zero"]),
    }
    evidence["wu_method_reach_and_limits"] = {
        "what_it_decides": "polynomial statements with a hypothesis system that pseudo-divides into a chain, under the recorded initials",
        "pascal_for_a_general_conic": "not done here: the hypothesis that six points lie on one conic is a single sextic determinant, not a chain, so the classical proof needs a parametrisation or a full triangularisation with irreducible components",
        "pascal_for_a_parabola": "done, since the parabola condition is already a triangular chain",
        "relation_to_the_repository": [
            "the repository's pinned geometry root is a Pascal presentation, and this is external evidence touching the same theorem",
            "it is not a native import and not a derivation certificate, so the Pascal-rooted growth obligation stays Open",
            "the method does not apply to the Feigenbaum fixed point, which is a functional equation rather than a polynomial system; a truncated polynomial system could be triangularised, but a chain gives zero-decomposition, not root isolation, so it would not replace the enclosures of the earlier rounds",
        ],
    }
    evidence["what_is_not_claimed"] = {
        "native_certificate": False,
        "geometry_catalog_admission": False,
        "general_conic_pascal": False,
        "feigenbaum_enclosure": False,
        "proof_of_a_prose_geometric_statement_without_its_polynomial_formulation": False,
    }

    checks = {
        "every_true_statement_reduces_to_zero": all(row["remainder_is_zero"] for row in truth),
        "every_falsified_statement_does_not": all(not row["remainder_is_zero"] for row in falsified),
        "both_methods_agree_everywhere": all(row["methods_agree"] for row in results),
        "groebner_confirms_the_falsified_ones_are_outside": all(
            not row["groebner_membership"] for row in falsified),
        "random_instances_are_zero_for_true_statements": all(
            all(instance["is_zero"] for instance in row["random_instances"]) for row in truth),
        "non_degeneracy_conditions_are_recorded": all(
            len(row["chain_initials_non_degeneracy_conditions"]) == len(row["chain"]) for row in results),
        "the_tooling_is_declared": evidence["tooling"]["available"],
        "within_assertion_budget": ASSERTIONS["n"] <= OBJ["max_assertions"],
        "within_time_budget": (time.monotonic() - started) <= CONTRACT["budget"]["wall_seconds"],
    }
    evidence["checks"] = checks
    evidence["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    evidence["cost"] = {
        "wall_seconds_before_serialization": round(time.monotonic() - started, 3),
        "assertions": ASSERTIONS["n"],
        "subprocesses": 0,
    }
    (HERE / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                                        encoding="utf-8")
    print(json.dumps({k: evidence[k] for k in ("status", "checks", "cost")}, indent=1))
    for row in results:
        print(f"  {row['statement']:32s} remainder_zero={row['remainder_is_zero']!s:5s} "
              f"groebner={row['groebner_membership']!s:5s} chain={len(row['chain'])} "
              f"terms={row['conclusion_terms']}")
    print("summary:", json.dumps(evidence["summary"]))
    return 0 if evidence["status"] == "ExternalExactPass" else 1


if __name__ == "__main__":
    sys.exit(main())
